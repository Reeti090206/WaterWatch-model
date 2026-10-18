"""
WaterWatch AI - Rainfall Model & Risk Baseline Evaluation Engine
Evaluates rainfall models or experimental risk baselines across geographic regions,
monsoon regimes, and rainfall severity strata, with specific validation for Nagpur.
"""

import os
import sys
import json
from pathlib import Path
import pandas as pd
import numpy as np
import joblib

sys.path.insert(0, str(Path(__file__).resolve().parent))
from rainfall_model_utils import ExperimentalMeteorologicalRiskBaseline, FEATURE_COLUMNS


PROJECT_ROOT = Path(__file__).resolve().parent.parent
DATA_DIR = PROJECT_ROOT / "data"
PROCESSED_DIR = DATA_DIR / "processed"
MODELS_DIR = PROJECT_ROOT / "models" / "rainfall"
REPORTS_DIR = PROJECT_ROOT / "reports"

REPORTS_DIR.mkdir(parents=True, exist_ok=True)


def evaluate_baseline_across_regions():
    print("=" * 60)
    print("EVALUATING RAINFALL RISK MODEL / BASELINE")
    print("=" * 60)

    # 1. Load model or baseline
    model_path = MODELS_DIR / "best_rainfall_model.joblib"
    baseline_path = MODELS_DIR / "experimental_risk_baseline.joblib"

    if model_path.exists():
        print(f"Loading supervised model from {model_path}...")
        model = joblib.load(model_path)
        is_supervised = True
    elif baseline_path.exists():
        print(f"Loading experimental baseline from {baseline_path}...")
        model = joblib.load(baseline_path)
        is_supervised = False
    else:
        raise FileNotFoundError("No model or baseline artifact found in models/rainfall/!")

    # 2. Load test features
    feat_path = PROCESSED_DIR / "rainfall_daily_features.csv"
    if not feat_path.exists():
        raise FileNotFoundError(f"Missing {feat_path}!")

    print(f"Loading daily features from {feat_path.name}...")
    df = pd.read_csv(feat_path)

    # Feature columns
    schema_path = MODELS_DIR / "feature_schema.json"
    with open(schema_path, "r", encoding="utf-8") as f:
        schema = json.load(f)
    feature_cols = schema["feature_columns"]

    X = df[feature_cols].fillna(0.0)

    # Compute risk scores
    if hasattr(model, "predict_risk"):
        df["predicted_risk_score"] = model.predict_risk(X)
    elif hasattr(model, "predict_proba"):
        df["predicted_risk_score"] = model.predict_proba(X)[:, 1]
    else:
        df["predicted_risk_score"] = model.predict(X)

    # 3. Stratified Evaluation by IMD Rainfall Category
    cat_eval = df.groupby("imd_category").agg(
        record_count=("rainfall_mm", "count"),
        mean_rainfall_mm=("rainfall_mm", "mean"),
        min_risk_score=("predicted_risk_score", "min"),
        mean_risk_score=("predicted_risk_score", "mean"),
        max_risk_score=("predicted_risk_score", "max")
    ).reset_index()

    # Sort categories hydrologically
    cat_order = ["No Rain", "Very Light", "Light", "Moderate", "Heavy", "Very Heavy", "Extremely Heavy"]
    cat_eval["cat_order"] = cat_eval["imd_category"].map(lambda x: cat_order.index(x) if x in cat_order else 99)
    cat_eval = cat_eval.sort_values("cat_order").drop(columns=["cat_order"])

    print("\n--- Stratified Evaluation by IMD Intensity ---")
    print(cat_eval.to_string(index=False))

    # 4. Regional Breakdown (Top Districts + Nagpur)
    reg_eval = df.groupby(["district_name", "is_nagpur"]).agg(
        record_count=("rainfall_mm", "count"),
        mean_daily_rainfall=("rainfall_mm", "mean"),
        max_daily_rainfall=("rainfall_mm", "max"),
        mean_risk_score=("predicted_risk_score", "mean"),
        high_risk_record_count=("predicted_risk_score", lambda s: (s >= 0.45).sum())
    ).reset_index()

    # Prioritize Nagpur
    reg_eval = reg_eval.sort_values(by=["is_nagpur", "mean_risk_score"], ascending=[False, False])
    print("\n--- Top Regional Risk Distribution (Nagpur Highlighted) ---")
    print(reg_eval.head(10).to_string(index=False))

    # Save evaluation summary
    eval_csv = REPORTS_DIR / "rainfall_model_evaluation_summary.csv"
    reg_eval.to_csv(eval_csv, index=False)
    print(f"\nSaved regional evaluation summary to {eval_csv}")

    # Sanity checks
    print("\nRunning Hydrological Monotonicity Sanity Check...")
    means = cat_eval["mean_risk_score"].tolist()
    is_monotonic = all(x <= y for x, y in zip(means, means[1:]))
    print(f"Monotonicity Check Passed: {is_monotonic} (Risk scores increase with rainfall intensity)")

    return reg_eval, cat_eval


def main():
    evaluate_baseline_across_regions()


if __name__ == "__main__":
    main()
