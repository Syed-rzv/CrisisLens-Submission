import pandas as pd
import logging
from werkzeug.utils import secure_filename

logger = logging.getLogger(__name__)

ALLOWED_EXTENSIONS = {'csv', 'xlsx', 'xls', 'json'}
MAX_FILE_SIZE = 250 * 1024 * 1024
MAX_ROWS = 500000

REQUIRED_COLUMNS = ['timestamp', 'description']

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def validate_file_size(file):
    file.seek(0, 2)
    size = file.tell()
    file.seek(0)
    
    if size > MAX_FILE_SIZE:
        return False, f"File too large. Max size: {MAX_FILE_SIZE / (1024*1024):.0f}MB"
    return True, None

def parse_upload(file, filename):
    try:
        ext = filename.rsplit('.', 1)[1].lower()
        
        if ext == 'csv':
            df = pd.read_csv(file)
        elif ext in ['xlsx', 'xls']:
            df = pd.read_excel(file)
        elif ext == 'json':
            df = pd.read_json(file)
        else:
            return None, "Unsupported file format"
        
        return df, None
    except Exception as e:
        logger.error(f"parse error: {str(e)}")
        return None, f"Failed to parse file: {str(e)}"

def validate_dataframe(df):
    errors = []
    warnings = []
    
    if len(df) == 0:
        errors.append("File is empty")
        return False, errors, warnings
    
    if len(df) > MAX_ROWS:
        errors.append(f"Too many rows. Max allowed: {MAX_ROWS:,}")
        return False, errors, warnings
    
    df.columns = df.columns.str.strip().str.lower()
    
    missing = [col for col in REQUIRED_COLUMNS if col not in df.columns]
    if missing:
        errors.append(f"Missing required columns: {', '.join(missing)}")
        return False, errors, warnings
    
    null_desc = df['description'].isnull().sum()
    if null_desc > 0:
        errors.append(f"{null_desc} rows have empty descriptions")
    
    if 'description' in df.columns:
        short_desc = df[df['description'].astype(str).str.len() < 10]
        if len(short_desc) > 0:
            warnings.append(f"{len(short_desc)} descriptions very short, classification accuracy may vary")
    
    try:
        df['timestamp'] = pd.to_datetime(df['timestamp'])
    except Exception as e:
        errors.append(f"Invalid timestamp format: {str(e)}")
    
    has_lat = 'latitude' in df.columns and df['latitude'].notna().any()
    has_lng = 'longitude' in df.columns and df['longitude'].notna().any()
    
    if has_lat != has_lng:
        warnings.append("Latitude/longitude mismatch in some records")
    
    return len(errors) == 0, errors, warnings

def needs_classification(df):
    return 'emergency_type' not in df.columns or df['emergency_type'].isnull().all()