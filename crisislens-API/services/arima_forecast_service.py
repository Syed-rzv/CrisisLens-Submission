import os
import logging
import argparse
import warnings
from datetime import datetime, timedelta
import pandas as pd
import numpy as np
from pmdarima import auto_arima
from statsmodels.tsa.arima.model import ARIMA
from sqlalchemy import create_engine, text
from dotenv import load_dotenv

warnings.filterwarnings('ignore')

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__))) 
load_dotenv(os.path.join(BASE_DIR, ".env"))

DB_USER = os.getenv("DB_USER", "root")
DB_PASSWORD = os.getenv("DB_PASSWORD", "")
DB_HOST = os.getenv("DB_HOST", "localhost")
DB_PORT = os.getenv("DB_PORT", "3306")
DB_NAME = os.getenv("DB_NAME", "capstone")

DATABASE_URI = f"mysql+pymysql://{DB_USER}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_NAME}"

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s"
)

def get_engine():
    return create_engine(DATABASE_URI)

def fetch_historical_data(engine, emergency_type=None):
    #Load all historical data for training.
    if emergency_type:
        query = """SELECT DATE(timestamp) AS ds, COUNT(*) AS y
            FROM emergency_data WHERE emergency_type = :etype GROUP BY DATE(timestamp) ORDER BY ds"""
        params = {"etype": emergency_type}
    else:
        query = """SELECT DATE(timestamp) AS ds, COUNT(*) AS y
            FROM emergency_data GROUP BY DATE(timestamp) ORDER BY ds"""
        params = {}
    
    with engine.connect() as conn:
        df = pd.read_sql(text(query), conn, params=params)
    
    return df

def find_arima_order(series):
    #Auto-select ARIMA parameters.
    try:
        model = auto_arima(
            series,
            start_p=0, start_q=0,
            max_p=3, max_q=3,
            m=7,
            seasonal=True,
            D=1,  # seasonal difference
            trace=False,
            stepwise=True,
            suppress_warnings=True,
            error_action='ignore',
            maxiter=50
        )
        return model.order, model.seasonal_order
    except:
        # Fallback to non-seasonal if it fails
        logging.warning("Seasonal ARIMA failed, using non-seasonal")
        model = auto_arima(
            series,
            start_p=0, start_q=0,
            max_p=5, max_q=5,
            seasonal=False,
            stepwise=True,
            suppress_warnings=True,
            error_action='ignore'
        )
        return model.order, (0, 0, 0, 0)


def train_and_forecast(series, order, seasonal_order, periods=30):
    if seasonal_order != (0, 0, 0, 0):
        # SARIMA model
        from statsmodels.tsa.statespace.sarimax import SARIMAX
        model = SARIMAX(series, order=order, seasonal_order=seasonal_order)
    else:
        # Regular ARIMA
        model = ARIMA(series, order=order)

    fitted = model.fit()

    forecast = fitted.forecast(steps=periods)

    # Calculate confidence intervals
    forecast_obj = fitted.get_forecast(steps=periods)
    conf_int = forecast_obj.conf_int()

    return forecast, conf_int

def save_forecasts_to_db(engine, forecasts_data, emergency_type=None):
    #Save forecast results to database.
    delete_query = "DELETE FROM forecasted_calls WHERE emergency_type = :etype OR (:etype IS NULL AND emergency_type = 'Overall')"
    
    insert_query = """INSERT INTO forecasted_calls (forecast_date, predicted_calls, lower_bound, upper_bound, emergency_type, model_used, generated_at)
        VALUES (:fdate, :pred, :lower, :upper, :etype, :model, :gen_at)"""
    
    etype_label = emergency_type if emergency_type else "Overall"
    
    with engine.begin() as conn:
        conn.execute(text(delete_query), {"etype": etype_label})
        
        for row in forecasts_data:
            conn.execute(text(insert_query), {
                "fdate": row['date'],
                "pred": float(row['prediction']),
                "lower": float(row['lower']),
                "upper": float(row['upper']),
                "etype": etype_label,
                "model": "ARIMA",
                "gen_at": datetime.now()})

def generate_forecasts(engine, emergency_type=None, periods=30):
    #Main forecasting pipeline
    label = emergency_type if emergency_type else "Overall"
    
    logging.info(f"\nGenerating ARIMA forecast: {label}")
    
    df = fetch_historical_data(engine, emergency_type)
    
    if df.empty or len(df) < 60:
        logging.warning(f"Insufficient data for {label}")
        return False
    
    logging.info(f"Training on {len(df)} days of historical data")
    
    series = df['y'].values
    order, seasonal_order = find_arima_order(series)
    logging.info(f"Selected ARIMA order: {order}, Seasonal order: {seasonal_order}")
    
    predictions, conf_int = train_and_forecast(series, order, seasonal_order, periods)
    
    # Prepare forecast data
    last_date = pd.to_datetime(df['ds'].iloc[-1])
    forecast_dates = [last_date + timedelta(days=i+1) for i in range(periods)]
    
    forecasts_data = []
    for i in range(periods):
        forecasts_data.append({
            'date': forecast_dates[i].strftime('%Y-%m-%d'),
            'prediction': max(0, predictions[i]),
            'lower': max(0, conf_int[i, 0]),
            'upper': conf_int[i, 1]})
    
    save_forecasts_to_db(engine, forecasts_data, emergency_type)
    
    logging.info(f"Saved {len(forecasts_data)} forecasts for {label}")
    
    return True

def main():
    parser = argparse.ArgumentParser(description="ARIMA production forecasting service")
    parser.add_argument("--periods", type=int, default=30, help="Days to forecast")
    parser.add_argument("--by-type", action="store_true", help="Forecast each emergency type")
    args = parser.parse_args()
    
    engine = get_engine()
    
    logging.info("ARIMA forecast service starting")
    logging.info(f"Forecast horizon: {args.periods} days")
    
    # overall forecast
    generate_forecasts(engine, None, args.periods)
    
    # type-specific forecasts if requested
    if args.by_type:
        types = ['EMS', 'Fire', 'Traffic']
        logging.info(f"Generating forecasts for {len(types)} emergency types")
        
        for etype in types:
            generate_forecasts(engine, etype, args.periods)
    
    logging.info("\nARIMA forecast service complete")
    logging.info(f"Forecasts generated at {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")

if __name__ == "__main__":
    main()