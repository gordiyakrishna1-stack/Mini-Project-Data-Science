"""Generate a model training summary sheet for the AI pipeline."""

import argparse
from pathlib import Path
import pandas as pd

from config import OUTPUT_DIR
from train_lstm import train_lstm
from train_xgboost import train_xgboost

WAREHOUSE_DIR = OUTPUT_DIR / "warehouse"
MODEL_DIR = WAREHOUSE_DIR / "models"
SUMMARY_PATH = MODEL_DIR / "model_training_summary.csv"
SUMMARY_MD = MODEL_DIR / "model_training_summary.md"


def save_summary(results):
    MODEL_DIR.mkdir(parents=True, exist_ok=True)

    df = pd.DataFrame(results)
    df.to_csv(SUMMARY_PATH, index=False)

    with open(SUMMARY_MD, 'w', encoding='utf-8') as md_file:
        md_file.write('# Model Training Summary\n\n')
        for result in results:
            md_file.write(f"## {result['model_type']}\n")
            for key, value in result.items():
                if key != 'model_type':
                    md_file.write(f"- **{key.replace('_', ' ').title()}:** {value}\n")
            md_file.write('\n')

    print(f"\nModel training summary saved to: {SUMMARY_PATH}")
    print(f"Model training markdown sheet saved to: {SUMMARY_MD}")


def run_training_sheet(disease: str, look_back: int, epochs: int, batch_size: int, test_size: float, seed: int):
    print("\n=== Running Model Training Sheet ===")
    lstm_results = train_lstm(disease, look_back, epochs, batch_size)
    xgb_results = train_xgboost(test_size, seed)

    results = [lstm_results, xgb_results]
    save_summary(results)
    return results


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Train both AI models and create a model training summary sheet.')
    parser.add_argument('--disease', default='Influenza', help='Disease name for LSTM forecasting')
    parser.add_argument('--look_back', type=int, default=60, help='LSTM look-back window in months')
    parser.add_argument('--epochs', type=int, default=100, help='LSTM training epochs')
    parser.add_argument('--batch_size', type=int, default=32, help='LSTM batch size')
    parser.add_argument('--test_size', type=float, default=0.2, help='XGBoost test split ratio')
    parser.add_argument('--seed', type=int, default=42, help='Random state')
    args = parser.parse_args()
    run_training_sheet(args.disease, args.look_back, args.epochs, args.batch_size, args.test_size, args.seed)
