import os
import logging
import argparse
from datetime import datetime
import pandas as pd
import numpy as np
from prophet import Prophet
import matplotlib.pyplot as plt

# Import shared utilities
from utils import fetch_daily_calls, calculate_metrics, save_metrics_to_csv, get_engine, get_emergency_types

# Note: Prophet model built as initial baseline before utils.py existed
# Integrated fetch/metrics functions but kept Prophet-specific logic separate

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
    #Split data into train and test sets.
    if len(df) < test_days + 30:
        split_idx = int(len(df) * 0.8)
    else:
        split_idx = len(df) - test_days
    
    train = df.iloc[:split_idx].copy()
    test = df.iloc[split_idx:].copy()
    
    return train, test

def train_prophet_model(train_df):
    #Train Prophet model with default seasonality.
    model = Prophet(
        daily_seasonality=False,
        weekly_seasonality=True,
        yearly_seasonality=True,
        seasonality_mode='additive'
    )
    
    model.fit(train_df)
    return model

def plot_prophet_validation(train_df, test_df, predictions, emergency_type):
    #Plot validation results.
    plt.figure(figsize=(14, 6))
    
    plt.plot(train_df['ds'], train_df['y'], label='Training', color='blue', alpha=0.6)
    plt.plot(test_df['ds'], test_df['y'], label='Actual', color='green', linewidth=2)
    plt.plot(test_df['ds'], predictions, label='Predicted', color='red', linestyle='--', linewidth=2)
    
    plt.xlabel('Date')
    plt.ylabel('Call Volume')
    
    label = emergency_type if emergency_type else "Overall"
    plt.title(f'Prophet - {label} Validation')
    plt.legend()
    plt.grid(True, alpha=0.3)
    plt.tight_layout()
    
    filename = f"prophet_{label.lower()}_validation.png"
    plt.savefig(os.path.join(PLOT_DIR, filename), dpi=100)
    plt.close()

def run_prophet_experiment(engine, emergency_type=None, test_days=30):
    #Run Prophet baseline experiment with validation.
    label = emergency_type if emergency_type else "Overall"
    
    logging.info(f"\nProphet Baseline: {label}")
    
    df = fetch_daily_calls(engine, emergency_type)
    
    if df.empty or len(df) < 60:
        logging.warning(f"Insufficient data for {label}")
        return None
    
    logging.info(f"Fetched {len(df)} days of data")
    
    train_df, test_df = split_train_test(df, test_days)
    logging.info(f"Train: {len(train_df)} days, Test: {len(test_df)} days")
    
    model = train_prophet_model(train_df)
    logging.info("Model trained")
    
    future = model.make_future_dataframe(periods=len(test_df))
    forecast = model.predict(future)
    
    predictions = forecast.iloc[-len(test_df):]['yhat'].values
    actual = test_df['y'].values
    
    metrics = calculate_metrics(actual, predictions)
    logging.info(f"Validation - RMSE: {metrics['RMSE']}, MAE: {metrics['MAE']}, MAPE: {metrics['MAPE']}%")
    
    plot_prophet_validation(train_df, test_df, predictions, emergency_type)
    
    csv_path = os.path.join(METRICS_DIR, "model_comparison.csv")
    save_metrics_to_csv("Prophet_Baseline", emergency_type, metrics, csv_path)
    
    return metrics

def main():
    parser = argparse.ArgumentParser(description="Prophet baseline forecasting")
    parser.add_argument("--by-type", action="store_true", help="Run for each emergency type")
    parser.add_argument("--test-days", type=int, default=30, help="Test set size in days")
    args = parser.parse_args()
    
    engine = get_engine()
    
    logging.info("Prophet baseline experiment starting")
    
    run_prophet_experiment(engine, None, args.test_days)
    
    if args.by_type:
        types = get_emergency_types(engine)
        logging.info(f"\nRunning for {len(types)} emergency types: {types}")
        
        for etype in types:
            run_prophet_experiment(engine, etype, args.test_days)
    
    logging.info("\nProphet baseline complete")

if __name__ == "__main__":
    main()