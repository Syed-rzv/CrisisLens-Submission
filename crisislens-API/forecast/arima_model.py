import os
import logging
import argparse
import warnings
import pandas as pd
import numpy as np
from pmdarima import auto_arima
from statsmodels.tsa.arima.model import ARIMA

from utils import (
    fetch_daily_calls,
    get_emergency_types,
    calculate_metrics,
    plot_validation,
    save_metrics_to_csv,
    get_engine
)

warnings.filterwarnings('ignore')

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
RESULTS_DIR = os.path.join(BASE_DIR, "..", "forecast_results")
PLOT_DIR = os.path.join(RESULTS_DIR, "plots")
METRICS_DIR = os.path.join(RESULTS_DIR, "metrics")

os.makedirs(PLOT_DIR, exist_ok=True)
os.makedirs(METRICS_DIR, exist_ok=True)

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s"
)

def split_train_test(df, test_days=30):
    #Split time series into train/test sets.
    if len(df) < test_days + 30:
        split_idx = int(len(df) * 0.8)
    else:
        split_idx = len(df) - test_days
    
    train = df.iloc[:split_idx].copy()
    test = df.iloc[split_idx:].copy()
    
    return train, test

def find_arima_params(train_series):
    #Auto-select ARIMA parameters using AIC.
    model = auto_arima(
        train_series,
        start_p=0, start_q=0,
        max_p=5, max_q=5,
        seasonal=False,
        stepwise=True,
        suppress_warnings=True,
        error_action='ignore'
    )
    
    return model.order

def train_arima(train_series, order):
    #Train ARIMA model with given parameters.
    model = ARIMA(train_series, order=order)
    fitted = model.fit()
    return fitted

def generate_predictions(model, steps):
    #Generate multi-step ahead forecast.
    forecast = model.forecast(steps=steps)
    return forecast

def run_arima_experiment(engine, emergency_type=None, test_days=30):
    #Run ARIMA forecasting experiment.
    label = emergency_type if emergency_type else "Overall"
    
    logging.info(f"\nARIMA: {label}")
    
    df = fetch_daily_calls(engine, emergency_type)
    
    if df.empty or len(df) < 60:
        logging.warning(f"Insufficient data for {label}")
        return None
    
    logging.info(f"Loaded {len(df)} days")
    
    train_df, test_df = split_train_test(df, test_days)
    logging.info(f"Train: {len(train_df)} days, Test: {len(test_df)} days")
    
    train_series = train_df['y'].values
    
    order = find_arima_params(train_series)
    logging.info(f"Selected order: {order}")
    
    # Train model
    model = train_arima(train_series, order)
    
    # Generate predictions
    predictions = generate_predictions(model, len(test_df))
    actual = test_df['y'].values
    
    # Calculate metrics
    metrics = calculate_metrics(actual, predictions)
    logging.info(f"RMSE: {metrics['RMSE']}, MAE: {metrics['MAE']}, MAPE: {metrics['MAPE']}%")
    
    # Plot results
    plot_validation(train_df, test_df, predictions, "ARIMA", emergency_type, PLOT_DIR)
    
    
    csv_path = os.path.join(METRICS_DIR, "model_comparison.csv")
    save_metrics_to_csv("ARIMA", emergency_type, metrics, csv_path)
    
    return metrics

def main():
    parser = argparse.ArgumentParser(description="ARIMA forecasting")
    parser.add_argument("--by-type", action="store_true", help="Run for each emergency type")
    parser.add_argument("--test-days", type=int, default=30, help="Test set size")
    args = parser.parse_args()
    
    engine = get_engine()
    
    logging.info("ARIMA experiment starting")
    
    run_arima_experiment(engine, None, args.test_days)
    
    if args.by_type:
        types = get_emergency_types(engine)
        logging.info(f"Running for emergency types: {types}")
        
        for etype in types:
            run_arima_experiment(engine, etype, args.test_days)
    
    logging.info("\nARIMA experiment complete")

if __name__ == "__main__":
    main()