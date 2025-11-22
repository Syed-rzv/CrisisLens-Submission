import os
import pandas as pd
import numpy as np
from sqlalchemy import create_engine, text
from dotenv import load_dotenv
import matplotlib.pyplot as plt
from datetime import datetime
from sklearn.metrics import mean_squared_error, mean_absolute_error

load_dotenv()

DB_USER = os.getenv("DB_USER", "root")
DB_PASSWORD = os.getenv("DB_PASSWORD", "")
DB_HOST = os.getenv("DB_HOST", "localhost")
DB_PORT = os.getenv("DB_PORT", "3306")
DB_NAME = os.getenv("DB_NAME", "capstone")

def get_engine():
    uri = f"mysql+pymysql://{DB_USER}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_NAME}"
    return create_engine(uri)

def fetch_daily_calls(engine, emergency_type=None):  #Load daily call volumes from emergency_data table
    if emergency_type:
        query = "SELECT DATE(timestamp) AS ds, COUNT(*) AS y FROM emergency_data WHERE emergency_type = :etype GROUP BY DATE(timestamp) ORDER BY ds"
        params = {"etype": emergency_type}
    else:
        query = "SELECT DATE(timestamp) AS ds, COUNT(*) AS y FROM emergency_data GROUP BY DATE(timestamp) ORDER BY ds"
        params = {}
    
    with engine.connect() as conn:
        df = pd.read_sql(text(query), conn, params=params)
    
    return df

def get_emergency_types(engine):  #Get list of emergency types from database.
    query = "SELECT DISTINCT emergency_type FROM emergency_data WHERE emergency_type IS NOT NULL"
    
    with engine.connect() as conn:
        result = pd.read_sql(text(query), conn)
    
    return result['emergency_type'].tolist()

def calculate_metrics(y_true, y_pred):
    #Calculate forecast accuracy metrics.
    rmse = np.sqrt(mean_squared_error(y_true, y_pred))
    mae = mean_absolute_error(y_true, y_pred)
    
    # MAPE calculation with zero handling
    mask = y_true != 0
    mape = np.mean(np.abs((y_true[mask] - y_pred[mask]) / y_true[mask])) * 100 if mask.any() else 0
    
    return {
        'RMSE': round(rmse, 2),
        'MAE': round(mae, 2),
        'MAPE': round(mape, 2)
    }

def plot_validation(train_df, test_df, predictions, model_name, emergency_type, output_dir):
    #Plot training data, actual test data, and predictions.
    plt.figure(figsize=(14, 6))
    
    plt.plot(train_df['ds'], train_df['y'], label='Training Data', color='blue', alpha=0.6)
    plt.plot(test_df['ds'], test_df['y'], label='Actual', color='green', linewidth=2)
    plt.plot(test_df['ds'], predictions, label='Predicted', color='red', linestyle='--', linewidth=2)
    
    plt.xlabel('Date')
    plt.ylabel('Call Volume')
    
    label = emergency_type if emergency_type else "Overall"
    plt.title(f'{model_name} - {label} Validation')
    plt.legend()
    plt.grid(True, alpha=0.3)
    plt.tight_layout()
    
    filename = f"{model_name.lower().replace(' ', '_')}_{label.lower()}_validation.png"
    filepath = os.path.join(output_dir, filename)
    plt.savefig(filepath, dpi=100)
    plt.close()

def plot_forecast(historical_df, forecast_df, model_name, emergency_type, output_dir):
    #Plot historical data with future forecast.
    plt.figure(figsize=(14, 6))
    
    plt.plot(historical_df['ds'], historical_df['y'], label='Historical', color='blue', alpha=0.6)
    plt.plot(forecast_df['ds'], forecast_df['yhat'], label='Forecast', color='red', linewidth=2)
    
    if 'yhat_lower' in forecast_df.columns and 'yhat_upper' in forecast_df.columns:
        plt.fill_between(forecast_df['ds'], 
                        forecast_df['yhat_lower'], 
                        forecast_df['yhat_upper'], 
                        alpha=0.2, color='red', label='Confidence Interval')
    
    plt.xlabel('Date')
    plt.ylabel('Call Volume')
    
    label = emergency_type if emergency_type else "Overall"
    plt.title(f'{model_name} - {label} Forecast')
    plt.legend()
    plt.grid(True, alpha=0.3)
    plt.tight_layout()
    
    filename = f"{model_name.lower().replace(' ', '_')}_{label.lower()}_forecast.png"
    filepath = os.path.join(output_dir, filename)
    plt.savefig(filepath, dpi=100)
    plt.close()

def save_metrics_to_csv(model_name, emergency_type, metrics, csv_path):
    #Append metrics to comparison CSV.
    label = emergency_type if emergency_type else "Overall"
    
    new_row = pd.DataFrame([{
        'Model': model_name,
        'Emergency_Type': label,
        'RMSE': metrics['RMSE'],
        'MAE': metrics['MAE'],
        'MAPE': metrics['MAPE'],
        'Timestamp': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    }])
    
    if os.path.exists(csv_path):
        try:
            df = pd.read_csv(csv_path, encoding='utf-8-sig')
            df = pd.concat([df, new_row], ignore_index=True)
        except (UnicodeDecodeError, pd.errors.EmptyDataError):
            # Corrupted or empty file, start fresh
            df = new_row
    else:
        df = new_row
    
    df.to_csv(csv_path, index=False, encoding='utf-8')