from flask import Blueprint, request, jsonify
from werkzeug.utils import secure_filename
import logging
import pandas as pd
from datetime import datetime
import sys

sys.path.append('../')
from db_config import get_connection as get_db_connection
from utils.file_validator import (allowed_file, validate_file_size, parse_upload, validate_dataframe, needs_classification)
from utils.classifier_wrapper import BatchClassifier

logger = logging.getLogger(__name__)
upload_bp = Blueprint('upload', __name__)

CHUNK_SIZE = 10000
IMMEDIATE_THRESHOLD = 5000

classifier = None

def get_classifier():
    global classifier
    if classifier is None:
        classifier = BatchClassifier()
    return classifier

@upload_bp.route('/upload', methods=['POST'])
def upload_dataset():
    if 'file' not in request.files:
        return jsonify({'error': 'No file provided'}), 400
    
    file = request.files['file']
    if file.filename == '':
        return jsonify({'error': 'No file selected'}), 400
    
    filename = secure_filename(file.filename)
    
    if not allowed_file(filename):
        return jsonify({'error': 'Invalid file type. Use CSV, Excel, or JSON'}), 400
    
    valid_size, size_error = validate_file_size(file)
    if not valid_size:
        return jsonify({'error': size_error}), 400
    
    df, parse_error = parse_upload(file, filename)
    if parse_error:
        return jsonify({'error': parse_error}), 400
    
    is_valid, errors, warnings = validate_dataframe(df)
    if not is_valid:
        return jsonify({'error': errors[0], 'all_errors': errors}), 400
    
    needs_ml = needs_classification(df)
    
    logger.info(f"upload: {filename}, {len(df)} rows, ml={needs_ml}")
    
    if len(df) < IMMEDIATE_THRESHOLD:
        try:
            result = process_upload_sync(df, filename, needs_ml)
            return jsonify(result), 200
        except Exception as e:
            logger.error(f"processing failed: {str(e)}")
            return jsonify({'error': f'Processing failed: {str(e)}'}), 500
    else:
        preview_data = df.head(10).to_dict('records')
        
        stats = {
            'total_rows': len(df),
            'needs_classification': needs_ml,
            'warnings': warnings,
            'columns': list(df.columns)
        }
        
        if needs_ml:
            stats['message'] = 'File will be classified using ML models'
        
        return jsonify({
            'status': 'preview',
            'preview': preview_data,
            'statistics': stats,
            'filename': filename
        }), 200

@upload_bp.route('/upload/confirm', methods=['POST'])
def confirm_upload():
    data = request.json
    
    if 'filename' not in data:
        return jsonify({'error': 'Missing filename'}), 400
    
    return jsonify({
        'status': 'processing',
        'message': 'Upload queued for processing',
        'job_id': 'mock_job_123'
    }), 202

def process_upload_sync(df, filename, needs_ml):
    total_rows = len(df)
    chunks = [df[i:i+CHUNK_SIZE] for i in range(0, total_rows, CHUNK_SIZE)]
    
    logger.info(f"processing {len(chunks)} chunks")
    
    inserted_count = 0
    
    for idx, chunk in enumerate(chunks):
        if needs_ml:
            chunk = get_classifier().classify_dataframe(chunk)
        else:
            chunk['classification_method'] = 'Manual'
            chunk['classification_confidence'] = 1.0
        
        chunk['filename'] = filename
        chunk['uploaded_at'] = datetime.now()
        chunk['source'] = 'Uploaded'
        
        inserted = insert_chunk(chunk)
        inserted_count += inserted
        
        logger.info(f"chunk {idx+1}/{len(chunks)}: {inserted} rows")
    
    report = {
        'status': 'complete',
        'total_rows': total_rows,
        'inserted_rows': inserted_count,
        'filename': filename,
        'classification_method': 'ML' if needs_ml else 'Manual'
    }
    
    if needs_ml and 'needs_review' in df.columns:
        report['low_confidence_count'] = int(df['needs_review'].sum())
    
    return report

def insert_chunk(df):
    column_mapping = {
        'timestamp': 'timestamp', 
        'description': 'description',
        'latitude': 'latitude',
        'longitude': 'longitude',
        'district': 'district',
        'emergency_type': 'emergency_type',
        'emergency_subtype': 'emergency_subtype',
        'caller_age': 'caller_age',
        'caller_gender': 'caller_gender',
        'zipcode': 'zipcode',
        'classification_method': 'classification_method',
        'classification_confidence': 'classification_confidence',
        'filename': 'filename',
        'uploaded_at': 'uploaded_at',
        'source': 'source'
    }
    
    insert_cols = {k: v for k, v in column_mapping.items() if k in df.columns}
    df_insert = df[list(insert_cols.keys())].copy()
    df_insert.columns = list(insert_cols.values())
    
    df_insert = df_insert.where(pd.notna(df_insert), None)
    
    cols = ', '.join(df_insert.columns)
    placeholders = ', '.join(['%s'] * len(df_insert.columns))
    query = f"INSERT INTO uploaded_data ({cols}) VALUES ({placeholders})"
    
    with get_db_connection() as conn:
        cursor = conn.cursor()
        
        values = df_insert.values.tolist()
        cursor.executemany(query, values)
        conn.commit()
        
        return cursor.rowcount

@upload_bp.route('/upload/status/<job_id>', methods=['GET'])
def get_upload_status(job_id):
    return jsonify({
        'job_id': job_id,
        'status': 'processing',
        'progress': 45,
        'message': 'Processing chunk 4 of 10'
    })