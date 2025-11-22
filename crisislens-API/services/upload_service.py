import pandas as pd
from utils.column_mapper import detect_column_mapping
from utils.validators import clean_and_validate
from services.classification_service import classify_emergency, classify_subtype
from database import db
import logging

logger = logging.getLogger(__name__)

ALLOWED_EXTENSIONS = {'csv', 'xlsx', 'xls', 'json'}
MAX_FILE_SIZE = 50 * 1024 * 1024  # 50MB

def process_uploaded_file(file, filename, user_id):

    file_ext = filename.rsplit('.', 1)[1].lower()
    
    # Parse file based on type
    if file_ext == 'csv':
        df = pd.read_csv(file)
    elif file_ext in ['xlsx', 'xls']:
        df = pd.read_excel(file)
    elif file_ext == 'json':
        df = pd.read_json(file)
    else:
        raise ValueError(f"Unsupported file type: {file_ext}")
    
    # Validate columns
    required = ['timestamp', 'lat', 'lng', 'desc']
    column_mapping = detect_column_mapping(df.columns)
    df = df.rename(columns=column_mapping)
    
    missing = [col for col in required if col not in df.columns]
    if missing:
        raise ValueError(f"Missing columns: {missing}")
    
    # Clean and validate
    df = clean_and_validate(df)
    
    # Classify using ML
    df['emergency_type'] = df['desc'].apply(classify_emergency)
    df['emergency_subtype'] = df['desc'].apply(classify_subtype)
    df['source'] = 'user_upload'
    
    # Insert into database
    records_inserted = bulk_insert_calls(df)
    
    # Log action
    log_upload_action(user_id, filename, len(df), records_inserted)
    
    return {
        'success': True,
        'message': f'Successfully imported {records_inserted} records',
        'stats': {
            'total_records': len(df),
            'inserted': records_inserted,
            'duplicates_skipped': len(df) - records_inserted,
            'date_range': {
                'start': df['timestamp'].min().isoformat(),
                'end': df['timestamp'].max().isoformat()
            },
            'emergency_types': df['emergency_type'].value_counts().to_dict()
        }
    }


def bulk_insert_calls(df):
    """Insert dataframe records into database"""
    records = df.to_dict('records')
    
    query = """
        INSERT IGNORE INTO emergency_data 
        (timestamp, lat, lng, desc, emergency_type, emergency_subtype, source)
        VALUES (%s, %s, %s, %s, %s, %s, %s)
    """
    
    values = [
        (r['timestamp'], r['lat'], r['lng'], r['desc'], 
         r['emergency_type'], r['emergency_subtype'], r['source'])
        for r in records
    ]
    
    cursor = db.cursor()
    cursor.executemany(query, values)
    db.commit()
    
    return cursor.rowcount


def log_upload_action(user_id, filename, total_records, inserted):
    # Will implement when audit system is added
    logger.info(f"User {user_id} uploaded {filename}: {inserted}/{total_records} records")