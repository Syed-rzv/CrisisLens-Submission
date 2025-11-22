import mysql.connector
import logging
import os
from dotenv import load_dotenv

dotenv_path = os.path.join(os.path.dirname(__file__), '..', 'crisislens-api', '.env')
load_dotenv(dotenv_path)

DB_CONFIG = {
    'host': os.getenv('DB_HOST'),
    'user': os.getenv('DB_USER'),
    'password': os.getenv('DB_PASSWORD'),
    'database': os.getenv('DB_NAME')
}

def run_pipeline():
    logging.basicConfig(level=logging.INFO)
    try:
        conn = mysql.connector.connect(**DB_CONFIG)
        cursor = conn.cursor()

        cursor.execute("SELECT COUNT(*) FROM raw_calls")
        count = cursor.fetchone()[0]
        logging.info(f" raw_calls table contains {count} rows")

        cursor.close()
        conn.close()
    except Exception as e:
        logging.exception(f"Pipeline error: {e}")

if __name__ == '__main__':
    run_pipeline()
