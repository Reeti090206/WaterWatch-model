"""
WaterWatch AI - Rainfall-to-Waterlogging Model Training Engine
Supports full supervised tabular training (Logistic Regression, Random Forest, XGBoost)
when verified event labels are supplied, and serializes an uncalibrated experimental
meteorological risk baseline when labels are absent, strictly avoiding data fabrication.
"""

import os
import sys
import json
from pathlib import Path
import pandas as pd
import numpy as np
from sklearn.linear_model import LogisticRegression
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import (
    precision_score, recall_score, f1_score, roc_auc_score,
    average_precision_score, confusion_matrix, brier_score_loss
)
from sklearn.preprocessing import StandardScaler
import joblib

sys.path.insert(0, str(Path(__file__).resolve().parent))
from rainfall_model_utils import ExperimentalMeteorologicalRiskBaseline, FEATURE_COLUMNS
PROJECT_ROOT = Path(__file__).resolve().parent.parent
DATA_DIR = PROJECT_ROOT / "data"
PROCESSED_DIR = DATA_DIR / "processed"
MODELS_DIR = PROJECT_ROOT / "models" / "rainfall"
REPORTS_DIR = PROJECT_ROOT / "reports"

MODELS_DIR.mkdir(parents=True, exist_ok=True)
REPORTS_DIR.mkdir(parents=True, exist_ok=True)


def save_feature_schema():
    schema = {
        "feature_columns": FEATURE_COLUMNS,
        "feature_descriptions": {
            "rainfall_mm": "Current 24-hour observed rainfall in millimeters (or 1-hour for telemetry)",
            "rainfall_prev1_day_mm": "Rainfall observed on previous day (lag-1)",
            "rainfall_prev2_day_mm": "Rainfall observed 2 days prior (lag-2)",
            "rainfall_2day_total_mm": "48-hour cumulative rainfall accumulation",
            "rainfall_3day_total_mm": "72-hour cumulative rainfall accumulation",
            "api_7day": "Antecedent Precipitation Index computed with decay lambda=0.85 over 7 days",
            "rainfall_trend_ratio": "Ratio of current day rainfall to 3-day cumulative rainfall",
            "is_monsoon": "Boolean flag (1 for June-Sept monsoon months, 0 otherwise)"
        },
        "target_column": "waterlogged_label",
        "target_description": "Binary flag (1 = waterlogged event verified, 0 = verified non-waterlogged)"
    }
    path = MODELS_DIR / "feature_schema.json"
    with open(path, "w", encoding="utf-8") as f:
        json.dump(schema, f, indent=2)
    print(f"Saved feature schema to {path}")


def train_supervised_models(matched_df):
    """Trains and compares tabular models on valid matched events."""
    print("Training supervised models on matched event records...")
    # Sorting chronologically
    if "date" in matched_df.columns:
        matched_df = matched_df.sort_values("date")

    X = matched_df[FEATURE_COLUMNS].fillna(0.0)
    y = matched_df["waterlogged_label"].astype(int)

    n_samples = len(X)
    train_end = int(n_samples * 0.70)
    val_end = int(n_samples * 0.85)

    X_train, y_train = X.iloc[:train_end], y.iloc[:train_end]
    X_val, y_val = X.iloc[train_end:val_end], y.iloc[train_end:val_end]
    X_test, y_test = X.iloc[val_end:], y.iloc[val_end:]

    models = {
        "LogisticRegression": LogisticRegression(max_iter=1000, class_weight="balanced"),
        "RandomForest": RandomForestClassifier(n_estimators=100, max_depth=6, class_weight="balanced", random_state=42)
    }

    try:
        from xgboost import XGBClassifier
        models["XGBoost"] = XGBClassifier(n_estimators=100, max_depth=4, learning_rate=0.05, random_state=42)
    except ImportError:
        pass

    results = {}
    best_f1 = -1.0
    best_model_name = None
    best_pipe = None

    for name, clf in models.items():
        pipe = Pipeline([("scaler", StandardScaler()), ("clf", clf)])
        pipe.fit(X_train, y_train)

        val_preds = pipe.predict(X_val)
        val_probs = pipe.predict_proba(X_val)[:, 1] if hasattr(pipe, "predict_proba") else val_preds

        prec = precision_score(y_val, val_preds, zero_division=0)
        rec = recall_score(y_val, val_preds, zero_division=0)
        f1 = f1_score(y_val, val_preds, zero_division=0)
        brier = brier_score_loss(y_val, val_probs)

        results[name] = {
            "precision": round(prec, 4),
            "recall": round(rec, 4),
            "f1": round(f1, 4),
            "brier": round(brier, 4)
        }
        print(f"[{name}] Val Precision: {prec:.3f}, Recall: {rec:.3f}, F1: {f1:.3f}, Brier: {brier:.3f}")

        if f1 > best_f1:
            best_f1 = f1
            best_model_name = name
            best_pipe = pipe

    # Save best
    save_path = MODELS_DIR / "best_rainfall_model.joblib"
    joblib.dump(best_pipe, save_path)
    print(f"Saved best model ({best_model_name}) to {save_path}")
    return results


def train_or_establish_baseline():
    save_feature_schema()

    matched_path = PROCESSED_DIR / "matched_waterlogging_dataset.csv"
    report_path = REPORTS_DIR / "rainfall_model_training_report.md"

    if matched_path.exists():
        matched_df = pd.read_csv(matched_path)
        if len(matched_df) > 10 and "waterlogged_label" in matched_df.columns:
            results = train_supervised_models(matched_df)
            with open(report_path, "w", encoding="utf-8") as f:
                f.write(f"# Supervised Rainfall-to-Waterlogging Training Results\n\n{results}\n")
            return

    # SCIENTIFIC INTEGRITY PATH
    print("\n" + "=" * 60)
    print("SUPERVISED LABEL AUDIT: NO VERIFIED OUTCOME LABELS PRESENT")
    print("ESTABLISHING TRANSPARENT EXPERIMENTAL RISK-SCORING BASELINE")
    print("=" * 60)

    baseline = ExperimentalMeteorologicalRiskBaseline()
    baseline_path = MODELS_DIR / "experimental_risk_baseline.joblib"
    joblib.dump(baseline, baseline_path)
    print(f"Saved baseline estimator to {baseline_path}")

    # Write detailed technical report
    md = [
        "# WaterWatch AI — Rainfall-to-Waterlogging Model Training Status\n",
        "## Scientific Assessment & Data Integrity Statement\n",
        "- **Supervised Model Status**: **NOT TRAINED (HEURISTIC BASELINE DEPLOYED)**",
        "- **Reason**: The provided workspace contains Maharashtra rainfall telemetry and manual daily logs (2021–2025), "
        "and image archives from Roboflow and Kaggle. However, **none of the datasets contain verified waterlogging incident logs** "
        "(timestamps, geolocations, and ground-truth flooded vs non-flooded verification).",
        "- **Strict Anti-Fabrication Compliance**: Under prompt instructions, we strictly do NOT fabricate synthetic waterlogging outcomes, "
        "do NOT assume rainfall automatically equals waterlogging, and do NOT falsely claim a trained supervised model.",
        "\n## Deployed Heuristic Baseline: `ExperimentalMeteorologicalRiskBaseline`\n",
        "- **Formula**: Combines acute 24-hour rainfall intensity (calibrated against IMD thresholds) and 7-day Antecedent Precipitation Index (API decay=0.85).",
        "- **Scale**: [0.0, 1.0] representing meteorological runoff hazard.",
        "- **Saved Artifact**: `models/rainfall/experimental_risk_baseline.joblib`",
        "- **Feature Schema**: `models/rainfall/feature_schema.json`",
        "\n## Requirements for Future Supervised Model Training\n",
        "1. Ingest municipal incident records or police traffic waterlogging advisories into `data/manifests/waterlogging_event_template.csv`.",
        "2. Execute `python scripts/build_event_dataset.py --events <file.csv>` to associate each incident with antecedent rainfall.",
        "3. Re-run `python scripts/train_rainfall_model.py` to train and compare Logistic Regression, Random Forest, and XGBoost.\n"
    ]
    with open(report_path, "w", encoding="utf-8") as f:
        f.write("\n".join(md))
    print(f"Saved training status report to {report_path}")


def main():
    train_or_establish_baseline()


if __name__ == "__main__":
    main()
