"""Train an XGBoost classifier for outbreak risk classification."""

import argparse
from pathlib import Path
import numpy as np
import pandas as pd
import xgboost as xgb
from sklearn.preprocessing import LabelEncoder
from sklearn.model_selection import train_test_split
from sklearn.metrics import accuracy_score, precision_score, recall_score, f1_score, classification_report
from sqlalchemy import create_engine

from config import OUTPUT_DIR

WAREHOUSE_DIR = OUTPUT_DIR / "warehouse"
SILVER_DIR = WAREHOUSE_DIR / "silver"
MODEL_DIR = WAREHOUSE_DIR / "models"


def assign_risk(row, cfr_q1, cfr_q3, case_q1, case_q3):
    cfr = row.get('CFR', 0)
    cases = row.get('Reported_Cases', 0)
    if cfr >= cfr_q3 or cases >= case_q3:
        return 2
    if cfr >= cfr_q1 or cases >= case_q1:
        return 1
    return 0


def prepare_data(df: pd.DataFrame):
    df = df.copy()
    df['Disease'] = df['Disease'].astype(str).str.strip().str.title()
    df['Province'] = df['Province'].astype(str).str.strip().str.title()
    df['Season'] = df['Season'].astype(str).str.strip().str.title()
    df['Gender'] = df['Gender'].astype(str).str.strip().str.title()
    df['Age_Group'] = df['Age_Group'].astype(str).str.strip().str.title()

    cfr_q1, cfr_q3 = df['CFR'].quantile([0.25, 0.75])
    case_q1, case_q3 = df['Reported_Cases'].quantile([0.25, 0.75])
    df['Risk_Label'] = df.apply(assign_risk, axis=1, args=(cfr_q1, cfr_q3, case_q1, case_q3))

    encoders = {}
    for col in ['Disease', 'Province', 'Season', 'Gender', 'Age_Group']:
        le = LabelEncoder()
        df[col + '_enc'] = le.fit_transform(df[col].astype(str))
        encoders[col] = le

    feature_cols = [
        'Disease_enc', 'Province_enc', 'Season_enc', 'Gender_enc', 'Age_Group_enc',
        'Reported_Cases', 'Deaths', 'Recovered', 'Hospitalized', 'ICU_Admission',
        'Vaccinated', 'CFR', 'Recovery_Rate', 'Hospitalization_Rate', 'Year', 'Month'
    ]

    df_model = df[feature_cols + ['Risk_Label']].dropna()
    X = df_model[feature_cols]
    y = df_model['Risk_Label']
    return X, y, encoders


def train_xgboost(test_size: float, random_state: int):
    silver_files = list(SILVER_DIR.glob("*_silver.csv"))
    if not silver_files:
        raise FileNotFoundError("Silver dataset not found. Run silver_transform.py first.")

    silver_path = silver_files[0]
    df = pd.read_csv(silver_path)
    X, y, encoders = prepare_data(df)

    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=test_size, random_state=random_state, stratify=y
    )

    class_counts = y_train.value_counts().to_dict()
    weights = {cls: 1.0 / count for cls, count in class_counts.items()}
    sample_weights = y_train.map(weights)

    dtrain = xgb.DMatrix(X_train, label=y_train, weight=sample_weights)
    dval = xgb.DMatrix(X_test, label=y_test)

    params = {
        'objective': 'multi:softprob',
        'num_class': 3,
        'eval_metric': 'mlogloss',
        'eta': 0.1,
        'max_depth': 6,
        'subsample': 0.8,
        'colsample_bytree': 0.8,
        'seed': random_state,
        'verbosity': 0
    }

    model = xgb.train(
        params,
        dtrain,
        num_boost_round=200,
        evals=[(dval, 'validation')],
        early_stopping_rounds=20,
        verbose_eval=False
    )

    y_pred = np.argmax(model.predict(dval), axis=1)

    accuracy = accuracy_score(y_test, y_pred)
    precision = precision_score(y_test, y_pred, average='macro')
    recall = recall_score(y_test, y_pred, average='macro')
    f1 = f1_score(y_test, y_pred, average='macro')
    report = classification_report(y_test, y_pred, target_names=['Low', 'Medium', 'High'])

    print("\n[XGBoost Risk Classification] Model evaluation")
    print(f"  Accuracy:  {accuracy:.4f}")
    print(f"  Precision: {precision:.4f}")
    print(f"  Recall:    {recall:.4f}")
    print(f"  F1-Score:  {f1:.4f}")
    print("\nClassification Report:")
    print(report)

    MODEL_DIR.mkdir(parents=True, exist_ok=True)
    model_path = MODEL_DIR / "xgboost_risk_model.json"
    model.save_model(model_path)

    engine = create_engine(f"sqlite:///{WAREHOUSE_DIR / 'epidemic_warehouse.sqlite'}")
    df.to_sql("Gold_Risk_Input", engine, if_exists='replace', index=False)
    engine.dispose()

    print(f"\n  Model saved: {model_path}")
    print(f"  Gold risk input table saved: Gold_Risk_Input in the warehouse database")

    return {
        'model_type': 'XGBoost',
        'test_size': test_size,
        'seed': random_state,
        'accuracy': float(accuracy),
        'precision': float(precision),
        'recall': float(recall),
        'f1_score': float(f1),
        'model_path': str(model_path),
        'classification_report': report,
        'train_samples': int(len(y_train)),
        'test_samples': int(len(y_test))
    }


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Train an XGBoost outbreak risk classifier using the Silver layer.")
    parser.add_argument("--test_size", type=float, default=0.2, help="Test data split ratio")
    parser.add_argument("--seed", type=int, default=42, help="Random state")
    args = parser.parse_args()
    train_xgboost(args.test_size, args.seed)
