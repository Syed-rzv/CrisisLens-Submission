from flask import Flask, jsonify, request
from flask_cors import CORS
from db_config import get_connection
from datetime import datetime
import os
from dotenv import load_dotenv

from functools import lru_cache
from time import time 

# For background processing
from redis import Redis
from rq import Queue
import sys

from services.clustering import analyze_emergency_clusters
import pandas as pd

from routes.temporal_analysis import temporal_bp

from routes.data_upload import upload_bp
from routes.auth_routes import auth_bp


sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

#background processing function
from Classifier.production.tasks import process_emergency_call

#Config
dotenv_path = os.path.join(os.path.dirname(__file__), '.env')
load_dotenv(dotenv_path)

app = Flask(__name__)
CORS(app, resources={
    r"/*": {
        "origins": ["http://localhost:3000", "http://127.0.0.1:3000"],
        "methods": ["GET", "POST", "PUT", "DELETE", "OPTIONS"],
        "allow_headers": ["Content-Type", "Authorization"]
    }
})

app.register_blueprint(temporal_bp, url_prefix='/temporal')
app.register_blueprint(upload_bp)
app.register_blueprint(auth_bp, url_prefix='/auth')


# Redis connection + queue for enrichment jobs
redis_conn = Redis(host="redis", port=6379, db=0)
q = Queue("crisislens", connection=redis_conn)
# Home 
@app.route('/')
def home():
    return jsonify({"message": "CrisisLens API is running"})

# Emergency Calls Endpoints
@app.route('/calls', methods=['GET'])
def get_calls():
    try:
        page = max(int(request.args.get('page', 1)), 1)
        limit = min(max(int(request.args.get('limit', 100)), 1), 50000)
    except ValueError:
        return jsonify({"error": "Invalid 'page' or 'limit'"}), 400

    offset = (page - 1) * limit
    date = request.args.get('date')
    emergency_type = request.args.get('type')
    emergency_subtype = request.args.get('subtype')
    district = request.args.get('district')  # Frontend sends 'district'
    source_filter = request.args.get('source', 'all')

    # WHERE conditions (to handle both column names)
    where_conditions = []
    params = []

    if date:
        where_conditions.append("DATE(timestamp) = %s")
        params.append(date)
    if emergency_type:
        where_conditions.append("emergency_type = %s")
        params.append(emergency_type)
    if emergency_subtype:
        where_conditions.append("emergency_subtype = %s")
        params.append(emergency_subtype)

    # Build query based on source
    if source_filter == 'live':
        if district:
            where_conditions.append("district = %s")
            params.append(district)
        
        where_clause = " AND ".join(where_conditions) if where_conditions else "1=1"
        
        query = f"""
            SELECT 
                id, timestamp, emergency_type, emergency_subtype, 
                district, latitude, longitude, description,
                zipcode, address, priority_flag, caller_gender,
                caller_age, source, 'live' as data_source
            FROM enriched_calls 
            WHERE {where_clause}
            ORDER BY timestamp DESC 
            LIMIT %s OFFSET %s
        """
        
    elif source_filter == 'historical':
        # emergency_data uses 'township' column aliased as 'district'
        if district:
            where_conditions.append("township = %s")
            params.append(district)
        
        where_clause = " AND ".join(where_conditions) if where_conditions else "1=1"
        
        query = f"""
            SELECT 
                id, timestamp, emergency_type, emergency_subtype,
                township AS district, latitude, longitude, description, emergency_title,
                zipcode, address, priority_flag, caller_gender,
                caller_age, source, 'historical' as data_source
            FROM emergency_data 
            WHERE {where_clause}
            ORDER BY timestamp DESC 
            LIMIT %s OFFSET %s
        """
        
    else: 
        live_params = list(params) 
        historical_params = list(params)  

        live_where = list(where_conditions)
        historical_where = list(where_conditions)
    
    if district:
        live_where.append("district = %s")
        historical_where.append("township = %s")
        live_params.append(district)
        historical_params.append(district)
    
    # final WHERE clauses
    live_clause = " AND ".join(live_where) if live_where else "1=1"
    historical_clause = " AND ".join(historical_where) if historical_where else "1=1"
    
    query = f"""
        SELECT * FROM (
            SELECT 
                id, timestamp, emergency_type, emergency_subtype,
                district, latitude, longitude, description,
                NULL as emergency_title,
                zipcode, address, priority_flag, caller_gender,
                caller_age, source, 'live' as data_source
            FROM enriched_calls
            WHERE {live_clause}
            
            UNION ALL
            
            SELECT 
                id, timestamp, emergency_type, emergency_subtype,
                township AS district, latitude, longitude, description, emergency_title,
                zipcode, address, priority_flag, caller_gender,
                caller_age, source, 'historical' as data_source
            FROM emergency_data
            WHERE {historical_clause}
        ) AS combined_data
        ORDER BY timestamp DESC
        LIMIT %s OFFSET %s
    """
    
    # Combine: live_params + historical_params
    params = live_params + historical_params

    params.extend([limit, offset])

    try:
        with get_connection() as conn:
            with conn.cursor(dictionary=True) as cursor:
                cursor.execute(query, params)
                results = cursor.fetchall()

        return jsonify({
            "page": page, 
            "limit": limit, 
            "count": len(results), 
            "results": results
        })
    except Exception as e:
        print(f"Error in /calls: {str(e)}")
        return jsonify({"error": str(e)}), 500


@app.route('/calls/latest', methods=['GET'])
def get_latest_calls():
    limit = request.args.get('limit', 10)
    source_filter = request.args.get('source', 'all')
    
    try:
        limit = int(limit)
    except ValueError:
        limit = 10

    if source_filter == 'live':
        query = """
            SELECT 
                id, timestamp, emergency_type, emergency_subtype, 
                district, latitude, longitude, description, 
                caller_gender, caller_age, source,
                'live' as data_source
            FROM enriched_calls
            ORDER BY timestamp DESC 
            LIMIT %s
        """
    elif source_filter == 'historical':
        query = """
            SELECT 
                id, timestamp, emergency_type, emergency_subtype,
                township AS district, latitude, longitude, description,
                caller_gender, caller_age, source,
                'historical' as data_source
            FROM emergency_data
            ORDER BY timestamp DESC 
            LIMIT %s
        """
    else:  # all
        query = """
            SELECT * FROM (
                SELECT 
                    id, timestamp, emergency_type, emergency_subtype,
                    district, latitude, longitude, description,
                    caller_gender, caller_age, source,
                    'live' as data_source
                FROM enriched_calls
                
                UNION ALL
                
                SELECT 
                    id, timestamp, emergency_type, emergency_subtype,
                    township AS district, latitude, longitude, description,
                    caller_gender, caller_age, source,
                    'historical' as data_source
                FROM emergency_data
            ) AS combined
            ORDER BY timestamp DESC
            LIMIT %s
        """

    try:
        with get_connection() as conn:
            with conn.cursor(dictionary=True) as cursor:
                cursor.execute(query, (limit,))
                results = cursor.fetchall()

        return jsonify(results)
    except Exception as e:
        print(f"Error in /calls/latest: {str(e)}")
        return jsonify({"error": str(e)}), 500

@app.route('/calls', methods=['POST'])
def ingest_call():
    data = request.json

    print("Received data:", data)

    required_fields = ['timestamp', 'description', 'latitude', 'longitude', 'district', 'gender', 'age']

    if not data:
        return jsonify({"error": "Missing JSON payload"}), 400

    for field in required_fields:
        if field not in data:
            print(f"Missing field: {field}")
            return jsonify({"error": f"Missing field: {field}"}), 400
    try:
        iso_timestamp = data['timestamp']
        mysql_timestamp = datetime.fromisoformat(iso_timestamp.replace('Z', '+00:00')).strftime('%Y-%m-%d %H:%M:%S')
    except Exception as e:
        return jsonify({"error": f"Invalid timestamp format: {str(e)}"}), 400

    insert_query = """
        INSERT INTO raw_calls (timestamp, description, latitude, longitude, district, gender, age, caller_name, caller_number)
        VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
    """
    values = (
        mysql_timestamp, 
        data['description'], 
        data['latitude'], 
        data['longitude'],
        data['district'],  
        data['gender'], 
        data['age'],
        data.get('caller_name'), 
        data.get('caller_number')
    )

    try:
        with get_connection() as conn:
            with conn.cursor() as cursor:
                cursor.execute(insert_query, values)
                raw_id = cursor.lastrowid
                conn.commit()

                print(f" Inserted into raw_calls with ID: {raw_id}")  
                print(f"   caller_name: {data.get('caller_name')}")      
                print(f"   caller_number: {data.get('caller_number')}")  

        # Enqueue classification job in background
        job = q.enqueue(process_emergency_call, raw_id)
        print(f"Call {raw_id} enqueued for processing. Job ID: {job.id}")

        return jsonify({"message": "Call successfully ingested (enrichment pending)", "raw_id": raw_id}), 201
    except Exception as e:
        print(f" Database error: {str(e)}")  #debugging
        return jsonify({"error": str(e)}), 500


#Aggregated data for our timelline chart
@app.route('/timeline-aggregated', methods=['GET'])
def get_timeline_aggregated():
    try:
        emergency_type = request.args.get('emergency_type')
        start_date = request.args.get('start_date')
        end_date = request.args.get('end_date')
        
        query = """
            SELECT 
                DATE(timestamp) as date,
                COUNT(*) as count,
                emergency_type
            FROM emergency_data
            WHERE emergency_type IN ('EMS', 'Fire', 'Traffic')
        """
        
        params = []
        
        if emergency_type and emergency_type != 'all':
            query += " AND emergency_type = %s"
            params.append(emergency_type)
        
        if start_date:
            query += " AND DATE(timestamp) >= %s"
            params.append(start_date)
        
        if end_date:
            query += " AND DATE(timestamp) <= %s"
            params.append(end_date)
        
        query += """
            GROUP BY DATE(timestamp), emergency_type
            ORDER BY date
        """
        
        with get_connection() as conn:
            with conn.cursor(dictionary=True) as cursor:
                cursor.execute(query, params if params else None)
                results = cursor.fetchall()
        
        for row in results:
            row['date'] = row['date'].strftime('%Y-%m-%d')
        
        return jsonify(results), 200
        
    except Exception as e:
        print(f"Timeline aggregation error: {str(e)}")
        return jsonify({"error": str(e)}), 500

#Stats Endpoints 
@app.route('/stats/counts', methods=['GET'])
def get_type_counts():
    query = """
        SELECT emergency_type, emergency_subtype, COUNT(*) as count
        FROM emergency_data
        GROUP BY emergency_type, emergency_subtype
        ORDER BY count DESC
    """
    with get_connection() as conn:
        with conn.cursor(dictionary=True) as cursor:
            cursor.execute(query)
            results = cursor.fetchall()
    return jsonify(results)


@app.route('/stats/daily', methods=['GET'])
def get_daily_stats():
    query = """
        SELECT DATE(timestamp) AS date, COUNT(*) AS count
        FROM emergency_data
        GROUP BY DATE(timestamp)
        ORDER BY date
    """
    with get_connection() as conn:
        with conn.cursor(dictionary=True) as cursor:
            cursor.execute(query)
            results = cursor.fetchall()
    return jsonify(results)


@app.route('/stats/township', methods=['GET'])
def get_township_counts():
    query = """
        SELECT township, COUNT(*) AS count
        FROM emergency_data
        GROUP BY township
        ORDER BY count DESC
    """
    with get_connection() as conn:
        with conn.cursor(dictionary=True) as cursor:
            cursor.execute(query)
            results = cursor.fetchall()
    return jsonify(results)

cluster_cache = {"data": None, "timestamp": 0}
CACHE_DURATION = 300  # 5 minutes 

#Clustering Endpoints

@app.route('/clusters', methods=['GET'])
def get_clusters():
    #DBSCAN clustering analysis endpoint
    
    try:
        time_range = request.args.get('time_range', 'all')
        min_severity = request.args.get('min_severity', type=float)
        
        # Dashboard filter parameters
        emergency_types = request.args.get('emergency_types', '')
        start_date = request.args.get('start_date')
        end_date = request.args.get('end_date')
        district = request.args.get('district')
        
        cache_key = f"{time_range}_{min_severity}_{emergency_types}_{start_date}_{end_date}_{district}"
        
        if (cluster_cache["data"] and 
            cluster_cache["params"] == cache_key and 
            (time() - cluster_cache["timestamp"]) < CACHE_DURATION):
            return jsonify(cluster_cache["data"]), 200
        
        query = """
          SELECT latitude as lat, longitude as lon, 
           COALESCE(emergency_type, 'Unknown') as call_type,
           timestamp,
           CASE COALESCE(emergency_type, 'Unknown')
               WHEN 'Fire' THEN 9
               WHEN 'EMS' THEN 8
               WHEN 'Traffic' THEN 7
               ELSE 5
           END as severity
          FROM emergency_data
          WHERE latitude IS NOT NULL 
            AND longitude IS NOT NULL
        """
        
        conditions = []
        params = []
        
        if emergency_types:
            types_list = [t.strip() for t in emergency_types.split(',')]
            placeholders = ','.join(['%s'] * len(types_list))
            conditions.append(f"emergency_type IN ({placeholders})")
            params.extend(types_list)
        
        if start_date:
            conditions.append("timestamp >= %s")
            params.append(start_date)
        
        if end_date:
            conditions.append("timestamp <= %s")
            params.append(end_date)
        
        if district:
            conditions.append("district = %s")
            params.append(district)
        
        if conditions:
            query += " AND " + " AND ".join(conditions)
        
        query += " LIMIT 50000"
        
        with get_connection() as conn:
            with conn.cursor(dictionary=True) as cursor:
                cursor.execute(query, params)
                results = cursor.fetchall()
        
        df = pd.DataFrame(results)
        
        if df.empty:
            return jsonify({"error": "No data available for selected filters"}), 404
        
        if time_range == 'day':
            df = df.copy()
            df['hour'] = pd.to_datetime(df['timestamp']).dt.hour
            df = df[(df['hour'] >= 6) & (df['hour'] < 18)].copy()
        elif time_range == 'night':
            df = df.copy()
            df['hour'] = pd.to_datetime(df['timestamp']).dt.hour
            df = df[(df['hour'] < 6) | (df['hour'] >= 18)].copy()

        if df.empty:
            return jsonify({"error": "No data available for selected time range"}), 404
        
        results = analyze_emergency_clusters(df)
        
        if min_severity:
            results['clusters'] = [
                c for c in results['clusters'] 
                if c['severity_score'] >= min_severity
            ]
        
        cluster_cache["data"] = results
        cluster_cache["params"] = cache_key
        cluster_cache["timestamp"] = time()
        
        return jsonify(results), 200
        
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route('/clusters/heatmap-data', methods=['GET'])
def get_heatmap_data():
    #Endpoint for heatmap visualization - now accepts dashboard filters
    try:
        emergency_types = request.args.get('emergency_types', '')
        start_date = request.args.get('start_date')
        end_date = request.args.get('end_date')
        district = request.args.get('district')
        
        query = """
            SELECT latitude as lat, longitude as lon,
                   CASE emergency_type
                       WHEN 'Fire' THEN 0.9
                       WHEN 'Medical Emergency' THEN 0.85
                       WHEN 'Accident' THEN 0.7
                       WHEN 'Assault' THEN 0.75
                       WHEN 'Robbery' THEN 0.65
                       ELSE 0.4
                   END as intensity
            FROM emergency_data
            WHERE latitude IS NOT NULL AND longitude IS NOT NULL
        """
        
        conditions = []
        params = []
        
        if emergency_types:
            types_list = [t.strip() for t in emergency_types.split(',')]
            placeholders = ','.join(['%s'] * len(types_list))
            conditions.append(f"emergency_type IN ({placeholders})")
            params.extend(types_list)
        
        if start_date:
            conditions.append("timestamp >= %s")
            params.append(start_date)
        
        if end_date:
            conditions.append("timestamp <= %s")
            params.append(end_date)
        
        if district:
            conditions.append("district = %s")
            params.append(district)
        
        if conditions:
            query += " AND " + " AND ".join(conditions)
        
        query += " LIMIT 50000"
        
        with get_connection() as conn:
            with conn.cursor(dictionary=True) as cursor:
                cursor.execute(query, params)
                results = cursor.fetchall()
        
        heatmap_data = [
            [float(row['lat']), float(row['lon']), float(row['intensity'])]
            for row in results
        ]
        
        return jsonify({"data": heatmap_data}), 200
        
    except Exception as e:
        return jsonify({"error": str(e)}), 500

#Forecasting Endpoints 

@app.route('/forecasts', methods=['GET'])
def get_forecasts():
    #Gets ARIMA forecasts with historical comparison data.

    try:
        emergency_type = request.args.get('type', 'Overall')
        days = request.args.get('days', type=int)
        
        # Get forecast data
        forecast_query = """
            SELECT 
                forecast_date,
                predicted_calls,
                lower_bound,
                upper_bound,
                emergency_type,
                model_used,
                generated_at
            FROM forecasted_calls
            WHERE emergency_type = %s
            AND model_used = 'ARIMA'
            ORDER BY forecast_date ASC
        """
        
        forecast_params = [emergency_type]
        
        if days:
            forecast_query += " LIMIT %s"
            forecast_params.append(days)
        
        #last 30 days of historical data 
        historical_query = """
            SELECT 
                DATE(timestamp) as date,
                COUNT(*) as actual_calls
            FROM emergency_data
            WHERE (%s = 'Overall' OR emergency_type = %s)
            GROUP BY DATE(timestamp)
            ORDER BY date DESC
            LIMIT 30
        """
        
        with get_connection() as conn:
            with conn.cursor(dictionary=True) as cursor:
                # Fetch forecasts
                cursor.execute(forecast_query, forecast_params)
                forecasts = cursor.fetchall()
                
                # Fetch historical data
                cursor.execute(historical_query, [emergency_type, emergency_type])
                historical = cursor.fetchall()
        
        for row in forecasts:
            row['forecast_date'] = row['forecast_date'].strftime('%Y-%m-%d')
            row['generated_at'] = row['generated_at'].strftime('%Y-%m-%d %H:%M:%S')
        
        # Reverse historical to chronological order and format
        historical.reverse()
        for row in historical:
            row['date'] = row['date'].strftime('%Y-%m-%d')
        
        return jsonify({
            'success': True,
            'forecasts': forecasts,
            'historical': historical,
            'count': len(forecasts)
        }), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/forecast-summary', methods=['GET'])
def get_forecast_summary():
    
    #Gest summary statistics from forecasts. Returns average predictions, peak day, etc.
    
    try:
        emergency_type = request.args.get('type', 'Overall')
        
        query = """
            SELECT 
                AVG(predicted_calls) as avg_predicted,
                MAX(predicted_calls) as max_predicted,
                MIN(predicted_calls) as min_predicted,
                MIN(forecast_date) as start_date,
                MAX(forecast_date) as end_date,
                COUNT(*) as total_days
            FROM forecasted_calls
            WHERE emergency_type = %s
            AND model_used = 'ARIMA'
        """
        
        with get_connection() as conn:
            with conn.cursor(dictionary=True) as cursor:
                cursor.execute(query, [emergency_type])
                summary = cursor.fetchone()
                
                # Get peak day
                cursor.execute("""
                    SELECT forecast_date, predicted_calls
                    FROM forecasted_calls
                    WHERE emergency_type = %s
                    AND model_used = 'ARIMA'
                    ORDER BY predicted_calls DESC
                    LIMIT 1
                """, [emergency_type])
                peak_day = cursor.fetchone()
        
        if summary:
            summary['start_date'] = summary['start_date'].strftime('%Y-%m-%d')
            summary['end_date'] = summary['end_date'].strftime('%Y-%m-%d')
            summary['avg_predicted'] = round(summary['avg_predicted'], 1)
            summary['max_predicted'] = round(summary['max_predicted'], 1)
            summary['min_predicted'] = round(summary['min_predicted'], 1)
            
            if peak_day:
                summary['peak_day'] = peak_day['forecast_date'].strftime('%Y-%m-%d')
                summary['peak_calls'] = round(peak_day['predicted_calls'], 1)
        
        return jsonify({
            'success': True,
            'summary': summary
        }), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

# Anomaly Endpoints 

@app.route('/anomalies', methods=['GET'])
def get_anomalies():
    try:
        from db_config import get_connection
        
        with get_connection() as conn:
            cursor = conn.cursor(dictionary=True)
            
            limit = request.args.get('limit', 100, type=int)
            severity = request.args.get('severity', None)
            
            query = "SELECT date, actual_calls, anomaly_score, severity, reason FROM anomaly_events"
            
            if severity:
                query += f" WHERE severity = '{severity}'"
            
            query += " ORDER BY date DESC LIMIT %s"
            
            cursor.execute(query, (limit,))
            anomalies = cursor.fetchall()
            cursor.close()
            
        return jsonify(anomalies), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

# Entry Point
if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=False)
