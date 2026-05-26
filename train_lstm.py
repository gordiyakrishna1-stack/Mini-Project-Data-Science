"""Train an LSTM model on monthly disease incidence data from the Silver layer."""

import argparse
from pathlib import Path
import numpy as np
import pandas as pd
from sklearn.preprocessing import MinMaxScaler
from sklearn.metrics import mean_squared_error, mean_absolute_error
from tensorflow.keras.models import Sequential
from tensorflow.keras.layers import LSTM, Dense, Dropout
from tensorflow.keras.callbacks import EarlyStopping
import matplotlib.pyplot as plt

from config import OUTPUT_DIR

WAREHOUSE_DIR = OUTPUT_DIR / "warehouse"
SILVER_DIR = WAREHOUSE_DIR / "silver"
MODEL_DIR = WAREHOUSE_DIR / "models"


def create_sequences(data: np.ndarray, look_back: int):
    X, y = [], []
    for i in range(len(data) - look_back):
        X.append(data[i:i + look_back])
        y.append(data[i + look_back])
    return np.array(X), np.array(y)


def load_disease_series(filepath: Path, disease: str):
    df = pd.read_csv(filepath)
    df = df[df['Disease'].str.strip().str.title() == disease.title()].copy()
    df = df.sort_values(['Year', 'Month'])
    monthly = df.groupby(['Year', 'Month'])['Reported_Cases'].sum().reset_index()
    if monthly.empty:
        raise ValueError(f"No data found for disease '{disease}' in silver layer.")
    return monthly


def train_lstm(disease: str, look_back: int, epochs: int, batch_size: int):
    silver_files = list(SILVER_DIR.glob("*_silver.csv"))
    if not silver_files:
        raise FileNotFoundError("Silver dataset not found. Run silver_transform.py first.")

    silver_path = silver_files[0]
    monthly = load_disease_series(silver_path, disease)
    MODEL_DIR.mkdir(parents=True, exist_ok=True)

    cases = monthly['Reported_Cases'].astype(float).values.reshape(-1, 1)
    scaler = MinMaxScaler()
    cases_scaled = scaler.fit_transform(cases)
    if len(cases_scaled) <= look_back:
        raise ValueError(
            f"Not enough monthly data for disease {disease}. "
            f"Found {len(cases_scaled)} months, need > {look_back}."
        )

    X, y = create_sequences(cases_scaled, look_back)
    split_idx = int(len(X) * 0.8)
    X_train, X_test = X[:split_idx], X[split_idx:]
    y_train, y_test = y[:split_idx], y[split_idx:]

    model = Sequential([
        LSTM(128, input_shape=(look_back, 1), return_sequences=True),
        Dropout(0.2),
        LSTM(64, return_sequences=False),
        Dropout(0.2),
        Dense(1)
    ])
    model.compile(optimizer='adam', loss='mse')
    model.summary()

    early_stop = EarlyStopping(monitor='val_loss', patience=10, restore_best_weights=True)
    history = model.fit(
        X_train, y_train,
        epochs=epochs,
        batch_size=batch_size,
        validation_data=(X_test, y_test),
        callbacks=[early_stop],
        verbose=2
    )

    y_pred_scaled = model.predict(X_test)
    y_pred = scaler.inverse_transform(y_pred_scaled)
    y_true = scaler.inverse_transform(y_test)

    rmse = np.sqrt(mean_squared_error(y_true, y_pred))
    mae = mean_absolute_error(y_true, y_pred)

    print(f"\nLSTM Forecast results for {disease}:")
    print(f"  Train samples: {len(X_train)}")
    print(f"  Test samples: {len(X_test)}")
    print(f"  RMSE: {rmse:.2f}")
    print(f"  MAE:  {mae:.2f}")

    model_path = MODEL_DIR / f"lstm_{disease.lower().replace(' ', '_')}_model.h5"
    scaler_path = MODEL_DIR / f"lstm_{disease.lower().replace(' ', '_')}_scaler.pkl"
    model.save(model_path)
    pd.Series(scaler.scale_.flatten(), name='scale').to_csv(scaler_path.replace('.pkl', '_scale.csv'), index=False)

    fig, ax = plt.subplots(figsize=(10, 5))
    ax.plot(y_true, label='Actual Cases')
    ax.plot(y_pred, label='Predicted Cases', linestyle='--')
    ax.set_title(f'LSTM {disease} Case Forecast')
    ax.set_xlabel('Test Month Index')
    ax.set_ylabel('Reported Cases')
    ax.legend()
    plot_path = MODEL_DIR / f"lstm_{disease.lower().replace(' ', '_')}_prediction.png"
    fig.savefig(plot_path, dpi=150, bbox_inches='tight')
    plt.close(fig)

    print(f"  Model saved: {model_path}")
    print(f"  Prediction chart saved: {plot_path}")

    return {
        'model_type': 'LSTM',
        'disease': disease,
        'look_back': look_back,
        'epochs': epochs,
        'batch_size': batch_size,
        'train_samples': len(X_train),
        'test_samples': len(X_test),
        'rmse': float(rmse),
        'mae': float(mae),
        'model_path': str(model_path),
        'prediction_plot': str(plot_path)
    }


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Train a Keras LSTM on the Silver layer monthly case counts.")
    parser.add_argument("--disease", default="Influenza", help="Disease name to forecast")
    parser.add_argument("--look_back", type=int, default=60, help="Number of months for look-back window")
    parser.add_argument("--epochs", type=int, default=100, help="Training epochs")
    parser.add_argument("--batch_size", type=int, default=32, help="Batch size")
    args = parser.parse_args()

    train_lstm(args.disease, args.look_back, args.epochs, args.batch_size)
