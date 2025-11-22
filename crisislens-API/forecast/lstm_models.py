import os
import logging
import argparse
import warnings
import pandas as pd
import numpy as np
import tensorflow as tf
from tensorflow import keras
from tensorflow.keras import layers
from sklearn.preprocessing import MinMaxScaler

from utils import (
    fetch_daily_calls,
    get_emergency_types,
    calculate_metrics,
    plot_validation,
    save_metrics_to_csv,
    get_engine
)

warnings.filterwarnings('ignore')
tf.get_logger().setLevel('ERROR')

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

def create_sequences(data, lookback=30):
    #Convert time series to supervised learning format.
    X, y = [], []
    for i in range(len(data) - lookback):
        X.append(data[i:i+lookback])
        y.append(data[i+lookback])
    return np.array(X), np.array(y)

def prepare_data(df, lookback=30, test_days=30):
    #Prepare data for LSTM training.
    values = df['y'].values.reshape(-1, 1)
    
    scaler = MinMaxScaler()
    scaled = scaler.fit_transform(values)
    
    split_idx = len(scaled) - test_days - lookback
    train_data = scaled[:split_idx + lookback]
    test_data = scaled[split_idx:]
    
    X_train, y_train = create_sequences(train_data, lookback)
    X_test, y_test = create_sequences(test_data, lookback)
    
    X_train = X_train.reshape((X_train.shape[0], X_train.shape[1], 1))
    X_test = X_test.reshape((X_test.shape[0], X_test.shape[1], 1))
    
    return X_train, y_train, X_test, y_test, scaler

def build_simple_lstm(lookback, units=50):
    #Single layer LSTM baseline.
    model = keras.Sequential([
        layers.LSTM(units, input_shape=(lookback, 1)),
        layers.Dense(1)
    ])
    model.compile(optimizer='adam', loss='mse')
    return model

def build_stacked_lstm(lookback, units=50):
    #Two-layer LSTM for increased capacity.
    model = keras.Sequential([
        layers.LSTM(units, return_sequences=True, input_shape=(lookback, 1)),
        layers.LSTM(units),
        layers.Dense(1)
    ])
    model.compile(optimizer='adam', loss='mse')
    return model

def train_model(model, X_train, y_train, X_test, y_test, epochs=50):
    #Train with early stopping to prevent overfitting.
    early_stop = keras.callbacks.EarlyStopping(
        monitor='val_loss',
        patience=10,
        restore_best_weights=True
    )
    
    history = model.fit(
        X_train, y_train,
        epochs=epochs,
        batch_size=16,
        validation_data=(X_test, y_test),
        callbacks=[early_stop],
        verbose=0
    )
    
    return history

def evaluate_model(model, X_test, y_test, scaler):
    #Generate predictions and inverse transform.
    predictions_scaled = model.predict(X_test, verbose=0)
    predictions = scaler.inverse_transform(predictions_scaled)
    actual = scaler.inverse_transform(y_test.reshape(-1, 1))
    
    return predictions.flatten(), actual.flatten()

def run_lstm_experiment(engine, emergency_type=None, architecture='simple', 
                       lookback=30, test_days=30, epochs=50):
    #Run LSTM experiment with specified architecture.
    label = emergency_type if emergency_type else "Overall"
    arch_name = architecture.capitalize()
    
    logging.info(f"\nLSTM ({arch_name}): {label}")
    
    df = fetch_daily_calls(engine, emergency_type)
    
    if df.empty or len(df) < lookback + test_days + 30:
        logging.warning(f"Insufficient data for {label}")
        return None
    
    logging.info(f"Loaded {len(df)} days")
    
    X_train, y_train, X_test, y_test, scaler = prepare_data(df, lookback, test_days)
    logging.info(f"Train: {len(X_train)} samples, Test: {len(X_test)} samples")
    
    if architecture == 'simple':
        model = build_simple_lstm(lookback)
    elif architecture == 'stacked':
        model = build_stacked_lstm(lookback)
    else:
        logging.error(f"Unknown architecture: {architecture}")
        return None
    
    logging.info(f"Training {arch_name} LSTM...")
    history = train_model(model, X_train, y_train, X_test, y_test, epochs)
    logging.info(f"Training complete ({len(history.history['loss'])} epochs)")
    
    predictions, actual = evaluate_model(model, X_test, y_test, scaler)
    
    metrics = calculate_metrics(actual, predictions)
    logging.info(f"RMSE: {metrics['RMSE']}, MAE: {metrics['MAE']}, MAPE: {metrics['MAPE']}%")
    
    test_start_idx = len(df) - test_days
    test_df = df.iloc[test_start_idx:].copy()
    train_df = df.iloc[:test_start_idx].copy()
    
    model_name = f"LSTM_{arch_name}"
    plot_validation(train_df, test_df, predictions, model_name, emergency_type, PLOT_DIR)
    
    csv_path = os.path.join(METRICS_DIR, "model_comparison.csv")
    save_metrics_to_csv(model_name, emergency_type, metrics, csv_path)
    
    return metrics

def main():
    parser = argparse.ArgumentParser(description="LSTM forecasting")
    parser.add_argument("--architecture", choices=['simple', 'stacked'], default='simple', help="LSTM architecture")
    parser.add_argument("--by-type", action="store_true",  help="Run for each emergency type")
    parser.add_argument("--test-days", type=int, default=30,  help="Test set size")
    parser.add_argument("--epochs", type=int, default=50, help="Training epochs")
    args = parser.parse_args()
    
    engine = get_engine()
    
    logging.info(f"LSTM experiment starting - {args.architecture} architecture")
    
    run_lstm_experiment(engine, None, args.architecture, test_days=args.test_days, epochs=args.epochs)
    
    if args.by_type:
        types = get_emergency_types(engine)
        logging.info(f"Running for emergency types: {types}")
        
        for etype in types:
            run_lstm_experiment(engine, etype, args.architecture,
                              test_days=args.test_days, epochs=args.epochs)
    
    logging.info("\nLSTM experiment complete")

if __name__ == "__main__":
    main()