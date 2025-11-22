import os
import sys
import pandas as pd
import numpy as np
import random
from sqlalchemy import create_engine, text
from dotenv import load_dotenv

def assign_age_group(age):
    if pd.isna(age):
        return None
    elif age <= 25:
        return '18-25'
    elif age <= 35:
        return '26-35'
    elif age <= 45:
        return '36-45'
    elif age <= 55:
        return '46-55'
    else:
        return '56+'

def get_db_connection():
    env_path = os.path.join(os.path.dirname(__file__), '..', 'crisislens-API', '.env')
    load_dotenv(env_path)
    
    db_user = os.getenv("DB_USER", "root")
    db_password = os.getenv("DB_PASSWORD", "")
    db_host = os.getenv("DB_HOST", "localhost")
    db_port = os.getenv("DB_PORT", "3306")
    db_name = os.getenv("DB_NAME", "capstone")
    
    uri = f"mysql+pymysql://{db_user}:{db_password}@{db_host}:{db_port}/{db_name}"
    return create_engine(uri)

def main():
    csv_path = os.path.join(os.path.dirname(__file__), 'cleaned_data_full.csv')
        
    if not os.path.exists(csv_path):
        print(f"Error: {csv_path} not found")
        sys.exit(1)
    
    print("Loading CSV...")
    df = pd.read_csv(csv_path)
    print(f"Loaded {len(df)} rows")
    
    print(f"\nDate range: {df['timestamp'].min()} to {df['timestamp'].max()}")
    
    df['year_temp'] = pd.to_datetime(df['timestamp']).dt.year
    print("\nRecords per year:")
    print(df['year_temp'].value_counts().sort_index())
    df.drop('year_temp', axis=1, inplace=True)
    
    print("\nGenerating synthetic demographics...")
    
    random.seed(42)
    df['caller_gender'] = [random.choice(['Male', 'Female']) for _ in range(len(df))]
    df['caller_age'] = [random.randint(18, 65) for _ in range(len(df))]
    df['age_group'] = df['caller_age'].apply(assign_age_group)
    df['source'] = 'kaggle'
    
    print(f"\nSample data:")
    print(df[['timestamp', 'emergency_type', 'caller_gender', 'caller_age', 'age_group']].head(3))
    
    print("\nConnecting to database...")
    engine = get_db_connection()
    
    print("Clearing emergency_data table...")
    with engine.begin() as conn:
        conn.execute(text("TRUNCATE TABLE emergency_data"))
    
    column_order = ['latitude', 'longitude', 'description', 'zipcode', 'emergency_title','timestamp', 'township', 'address', 'priority_flag', 
                    'emergency_type','emergency_subtype', 'caller_gender', 'caller_age','age_group', 'source']
    
    df_ordered = df[column_order]
    
    df_ordered = df_ordered.replace({np.nan: None})
    
    print(f"Loading {len(df_ordered)} rows in batches...")
    batch_size = 10000
    total_batches = (len(df_ordered) // batch_size) + 1
    
    for i in range(0, len(df_ordered), batch_size):
        batch_num = (i // batch_size) + 1
        batch = df_ordered.iloc[i:i+batch_size]
        
        batch.to_sql('emergency_data', engine, if_exists='append', index=False)
        print(f"Batch {batch_num}/{total_batches} ({len(batch)} rows)")
    
    print("\nVerifying load...")
    with engine.connect() as conn:
        result = conn.execute(text("SELECT COUNT(*) FROM emergency_data"))
        count = result.fetchone()[0]
        
        result = conn.execute(text("SELECT MIN(timestamp), MAX(timestamp) FROM emergency_data"))
        dates = result.fetchone()
        
        result = conn.execute(text("SELECT emergency_type, COUNT(*) FROM emergency_data GROUP BY emergency_type"))
        types = result.fetchall()
    
    print(f"\n✓ Successfully loaded {count} rows")
    print(f"Date range: {dates[0]} to {dates[1]}")
    print("\nEmergency type distribution:")
    for t, c in types:
        print(f"  {t}: {c:,}")
    
    print("\nDone!")

if __name__ == "__main__":
    main()