import pandas as pd
import numpy as np
from sklearn.ensemble import IsolationForest
from datetime import datetime
import mysql.connector
import os
from dotenv import load_dotenv

load_dotenv()

def connect_db():
    return mysql.connector.connect(
        host=os.getenv('DB_HOST'),
        user=os.getenv('DB_USER'),
        password=os.getenv('DB_PASSWORD'),
        database=os.getenv('DB_NAME')
    )

def prepare_features():
    #Extract daily features for anomaly detection
    conn = connect_db()
    
    # Daily aggregates with type breakdown
    query = """SELECT DATE(timestamp) as date, COUNT(*) as total_calls, SUM(CASE WHEN emergency_type = 'EMS' THEN 1 ELSE 0 END) as ems_calls, 
    SUM(CASE WHEN emergency_type = 'Fire' THEN 1 ELSE 0 END) as fire_calls,
    SUM(CASE WHEN emergency_type = 'Traffic' THEN 1 ELSE 0 END) as traffic_calls
    FROM emergency_data WHERE timestamp IS NOT NULL GROUP BY DATE(timestamp) ORDER BY date"""
    df = pd.read_sql(query, conn)
    
    # Peak hour detection
    hourly_query = """SELECT DATE(timestamp) as date, HOUR(timestamp) as hour, COUNT(*) as hourly_calls
    FROM emergency_data WHERE timestamp IS NOT NULL GROUP BY DATE(timestamp), HOUR(timestamp)"""
    hourly_df = pd.read_sql(hourly_query, conn)
    peak_hours = hourly_df.groupby('date')['hourly_calls'].max().reset_index()
    peak_hours.columns = ['date', 'peak_hour_calls']
    
    # Nighttime activity (11pm-6am)
    night_query = """SELECT DATE(timestamp) as date, COUNT(*) as night_calls 
    FROM emergency_data WHERE timestamp IS NOT NULL AND (HOUR(timestamp) >= 23 OR HOUR(timestamp) < 6) GROUP BY DATE(timestamp)"""
    night_df = pd.read_sql(night_query, conn)
    conn.close()
    
    # Merge all features
    df = df.merge(peak_hours, on='date', how='left')
    df = df.merge(night_df, on='date', how='left')
    df['night_calls'] = df['night_calls'].fillna(0)
    
    # Calculate percentages
    df['ems_pct'] = (df['ems_calls'] / df['total_calls'] * 100).round(2)
    df['fire_pct'] = (df['fire_calls'] / df['total_calls'] * 100).round(2)
    df['traffic_pct'] = (df['traffic_calls'] / df['total_calls'] * 100).round(2)
    df['night_pct'] = (df['night_calls'] / df['total_calls'] * 100).round(2)
    
    return df

def detect_anomalies(df):
    features = ['total_calls', 'ems_pct', 'fire_pct', 'traffic_pct', 'peak_hour_calls', 'night_pct']
    X = df[features].values
    
    # Contamination set to 5% 
    iso_forest = IsolationForest(
        contamination=0.05,
        random_state=42,
        n_estimators=100
    )
    
    df['anomaly'] = iso_forest.fit_predict(X)
    df['anomaly_score'] = iso_forest.score_samples(X)
    df['is_anomaly'] = df['anomaly'] == -1
    
    anomalies = df[df['is_anomaly']].copy()
    
    if len(anomalies) > 0:
        score_threshold = anomalies['anomaly_score'].median()
        anomalies['severity'] = anomalies['anomaly_score'].apply(
            lambda x: 'High' if x < score_threshold else 'Medium'
        )
    
    return anomalies

def get_anomaly_reason(row):
    #why this day was flagged
    reasons = []
    
    if row['total_calls'] > 600:
        reasons.append(f"High volume ({int(row['total_calls'])} calls)")
    elif row['total_calls'] < 200:
        reasons.append(f"Low volume ({int(row['total_calls'])} calls)")
    
    if row['fire_pct'] > 25:
        reasons.append(f"High fire calls ({row['fire_pct']:.1f}%)")
    if row['traffic_pct'] > 40:
        reasons.append(f"High traffic incidents ({row['traffic_pct']:.1f}%)")
    if row['ems_pct'] < 50:
        reasons.append(f"Low EMS percentage ({row['ems_pct']:.1f}%)")
    
    if row['night_pct'] > 15:
        reasons.append(f"Unusual nighttime activity ({row['night_pct']:.1f}%)")
    
    return "; ".join(reasons) if reasons else "Unusual call pattern detected"

def save_to_db(anomalies):
    conn = connect_db()
    cursor = conn.cursor()
    
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS anomaly_events (
        id INT AUTO_INCREMENT PRIMARY KEY,
        date DATE NOT NULL,
        actual_calls INT,
        anomaly_score FLOAT,
        severity VARCHAR(20),
        reason TEXT,
        detected_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        UNIQUE KEY unique_date (date)
    )
    """)
    
    cursor.execute("DELETE FROM anomaly_events")
    
    for _, row in anomalies.iterrows():
        reason = get_anomaly_reason(row)
        cursor.execute("INSERT INTO anomaly_events (date, actual_calls, anomaly_score, severity, reason) VALUES (%s, %s, %s, %s, %s)", (
            row['date'],
            int(row['total_calls']),
            float(row['anomaly_score']),
            row['severity'],
            reason
))
    
    conn.commit()
    cursor.close()
    conn.close()

def main():
    print("Loading emergency call data...")
    df = prepare_features()
    print(f"Analyzing {len(df)} days")
    
    print("Running isolation forest detection...")
    anomalies = detect_anomalies(df)
    pct = len(anomalies)/len(df)*100 if len(df) > 0 else 0
    print(f"Found {len(anomalies)} anomalies ({pct:.1f}%)")
    
    if len(anomalies) > 0:
        print("\nTop anomalies:")
        top = anomalies.nsmallest(10, 'anomaly_score')[['date', 'total_calls', 'severity']]
        print(top.to_string(index=False))
        
        print("\nSaving to database...")
        save_to_db(anomalies)
        print("Done")
    else:
        print("No anomalies detected")

if __name__ == "__main__":
    main()