from flask import Blueprint, jsonify, request
from datetime import datetime, timedelta
import mysql.connector
from mysql.connector import Error
import os
from dotenv import load_dotenv

load_dotenv()

temporal_bp = Blueprint('temporal', __name__)

def get_db_connection():
    try:
        connection = mysql.connector.connect(
            host=os.getenv('DB_HOST', 'localhost'),
            database=os.getenv('DB_NAME', 'capstone'),
            user=os.getenv('DB_USER', 'root'),
            password=os.getenv('DB_PASSWORD', '')
        )
        return connection
    except Error as e:
        print(f"Database connection error: {e}")
        return None

@temporal_bp.route('/peak-hours', methods=['GET'])
def get_peak_hours():
    #Returns call volume grouped by hour of day and day of week.
    connection = get_db_connection()
    if not connection:
        return jsonify({'error': 'Database connection failed'}), 500
    
    try:
        cursor = connection.cursor(dictionary=True)
        
        # Get date range filters if provided
        start_date = request.args.get('start_date')
        end_date = request.args.get('end_date')
        emergency_type = request.args.get('type')
        
        query = "SELECT HOUR(timestamp) as hour,DAYOFWEEK(timestamp) as day_of_week, COUNT(*) as call_count FROM emergency_data WHERE 1=1"
        params = []
        
        if start_date:
            query += " AND DATE(timestamp) >= %s"
            params.append(start_date)
        if end_date:
            query += " AND DATE(timestamp) <= %s"
            params.append(end_date)
        if emergency_type:
            query += " AND emergency_type = %s"
            params.append(emergency_type)
            
        query += """
            GROUP BY hour, day_of_week
            ORDER BY day_of_week, hour
        """
        
        cursor.execute(query, params)
        results = cursor.fetchall()
        
        # Transform into heatmap-friendly format
        heatmap_data = {}
        for row in results:
            day = row['day_of_week']
            hour = row['hour']
            count = row['call_count']
            
            if day not in heatmap_data:
                heatmap_data[day] = {}
            heatmap_data[day][hour] = count
        
        return jsonify({
            'success': True,
            'data': heatmap_data,
            'metadata': {
                'total_records': len(results),
                'filters_applied': {
                    'start_date': start_date,
                    'end_date': end_date,
                    'type': emergency_type
                }
            }
        })
        
    except Error as e:
        return jsonify({'error': str(e)}), 500
    finally:
        if connection.is_connected():
            cursor.close()
            connection.close()

@temporal_bp.route('/seasonal-trends', methods=['GET'])
def get_seasonal_trends():
   # Returns monthly aggregated call volumes over time.
    
    connection = get_db_connection()
    if not connection:
        return jsonify({'error': 'Database connection failed'}), 500
    
    try:
        cursor = connection.cursor(dictionary=True)
        
        emergency_type = request.args.get('type')
        
        query = "SELECT YEAR(timestamp) as year, MONTH(timestamp) as month, emergency_type, COUNT(*) as call_count FROM emergency_data WHERE 1=1"
        params = []
        
        if emergency_type:
            query += " AND emergency_type = %s"
            params.append(emergency_type)
            
        query += """
            GROUP BY year, month, emergency_type
            ORDER BY year, month
        """
        
        cursor.execute(query, params)
        results = cursor.fetchall()
        
        # Organize by type for easier charting
        trends_by_type = {}
        for row in results:
            etype = row['emergency_type']
            if etype not in trends_by_type:
                trends_by_type[etype] = []
            
            trends_by_type[etype].append({
                'year': row['year'],
                'month': row['month'],
                'count': row['call_count'],
                'date': f"{row['year']}-{row['month']:02d}"
            })
        
        return jsonify({
            'success': True,
            'data': trends_by_type,
            'metadata': {
                'total_months': len(results),
                'emergency_types': list(trends_by_type.keys())
            }
        })
        
    except Error as e:
        return jsonify({'error': str(e)}), 500
    finally:
        if connection.is_connected():
            cursor.close()
            connection.close()

@temporal_bp.route('/type-patterns', methods=['GET'])
def get_type_patterns():
    
    #Returns hourly distribution for each emergency type.
    
    connection = get_db_connection()
    if not connection:
        return jsonify({'error': 'Database connection failed'}), 500
    
    try:
        cursor = connection.cursor(dictionary=True)
        
        query = """
            SELECT emergency_type, HOUR(timestamp) as hour, COUNT(*) as call_count, ROUND(COUNT(*) * 100.0 / SUM(COUNT(*)) OVER (PARTITION BY emergency_type), 2) as percentage
            FROM emergency_data GROUP BY emergency_type, hour ORDER BY emergency_type, hour
        """
        
        cursor.execute(query)
        results = cursor.fetchall()
        
        # Group by emergency type
        patterns = {}
        for row in results:
            etype = row['emergency_type']
            if etype not in patterns:
                patterns[etype] = []
            
            patterns[etype].append({
                'hour': row['hour'],
                'count': row['call_count'],
                'percentage': float(row['percentage'])
            })
        
        return jsonify({
            'success': True,
            'data': patterns,
            'metadata': {
                'emergency_types': list(patterns.keys())
            }
        })
        
    except Error as e:
        return jsonify({'error': str(e)}), 500
    finally:
        if connection.is_connected():
            cursor.close()
            connection.close()

@temporal_bp.route('/summary-stats', methods=['GET'])
def get_summary_stats():
    """
    Returns high-level temporal statistics for dashboard summary cards.
    Includes busiest hour, busiest day, average daily calls, etc.
    """
    connection = get_db_connection()
    if not connection:
        return jsonify({'error': 'Database connection failed'}), 500
    
    try:
        cursor = connection.cursor(dictionary=True)
        
        # Busiest hour
        cursor.execute("""
            SELECT HOUR(timestamp) as hour, COUNT(*) as count
            FROM emergency_data GROUP BY hour ORDER BY count DESC LIMIT 1
        """)
        busiest_hour = cursor.fetchone()
        
        # Busiest day of week
        cursor.execute("""
            SELECT DAYOFWEEK(timestamp) as day, COUNT(*) as count
            FROM emergency_data GROUP BY day ORDER BY count DESC LIMIT 1
        """)
        busiest_day = cursor.fetchone()
        
        # Average daily calls
        cursor.execute("""
            SELECT AVG(daily_count) as avg_daily
            FROM (SELECT DATE(timestamp) as date, COUNT(*) as daily_count FROM emergency_data GROUP BY date) daily_stats
        """)
        avg_result = cursor.fetchone()
        
        # Day name mapping
        day_names = {1: 'Sunday', 2: 'Monday', 3: 'Tuesday', 4: 'Wednesday', 5: 'Thursday', 6: 'Friday', 7: 'Saturday'}
        
        return jsonify({
            'success': True,
            'data': {
                'busiest_hour': {
                    'hour': busiest_hour['hour'],
                    'count': busiest_hour['count'],
                    'label': f"{busiest_hour['hour']}:00"
                },
                'busiest_day': {
                    'day': busiest_day['day'],
                    'count': busiest_day['count'],
                    'label': day_names.get(busiest_day['day'], 'Unknown')
                },
                'average_daily_calls': round(avg_result['avg_daily'], 2) if avg_result['avg_daily'] else 0
            }
        })
        
    except Error as e:
        return jsonify({'error': str(e)}), 500
    finally:
        if connection.is_connected():
            cursor.close()
            connection.close()