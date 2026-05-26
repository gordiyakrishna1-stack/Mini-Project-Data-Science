"""End-to-end AI pipeline wrapper for medallion ETL and model training."""

import argparse
import sys


def run_pipeline(disease: str, look_back: int, epochs: int, batch_size: int, test_size: float, seed: int):
    print("\n=== Starting AI Pipeline ===")

    commands = [
        ("Bronze ingestion", [sys.executable, "bronze_ingestion.py"]),
        ("Silver transform", [sys.executable, "silver_transform.py"]),
        ("Gold aggregation", [sys.executable, "gold_aggregate.py"]),
        ("Train LSTM forecast model", [sys.executable, "train_lstm.py", "--disease", disease, "--look_back", str(look_back), "--epochs", str(epochs), "--batch_size", str(batch_size)]),
        ("Train XGBoost risk classifier", [sys.executable, "train_xgboost.py", "--test_size", str(test_size), "--seed", str(seed)])
    ]

    for label, cmd in commands:
        print(f"\n>>> {label}")
        exit_code = __import__('subprocess').run(cmd).returncode
        if exit_code != 0:
            raise SystemExit(f"Command failed: {' '.join(cmd)} (exit code {exit_code})")

    print("\n=== AI Pipeline Completed Successfully ===")


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Run the full AI medallion pipeline and model training.')
    parser.add_argument('--disease', default='Influenza', help='Disease name for LSTM forecasting')
    parser.add_argument('--look_back', type=int, default=60, help='LSTM look-back window in months')
    parser.add_argument('--epochs', type=int, default=100, help='LSTM training epochs')
    parser.add_argument('--batch_size', type=int, default=32, help='LSTM batch size')
    parser.add_argument('--test_size', type=float, default=0.2, help='XGBoost test split ratio')
    parser.add_argument('--seed', type=int, default=42, help='Random seed for reproducibility')
    args = parser.parse_args()

    run_pipeline(args.disease, args.look_back, args.epochs, args.batch_size, args.test_size, args.seed)
