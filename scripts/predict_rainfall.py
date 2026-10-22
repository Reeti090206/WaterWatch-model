"""
WaterWatch AI - Dual-Mode Rainfall Prediction & Hydrological Risk Inference Engine
Supports:
1. Experimental Supervised Prediction on 6-feature sub-daily telemetry (rainfall_1h_mm, 3h, 6h, 24h, 72h, drainage proxy)
   using the trained synthetic model (SYNTHETIC_EXPERIMENTAL).
2. Meteorological Risk Heuristic Baseline on daily rainfall telemetry (24h mm, lags, 7-day API)
   preserving backwards compatibility with the verified municipal pipeline.
3. Batch prediction generation across sample dataset rows, supported Nagpur localities, and illustrative scenarios.
"""

import os
import sys
import json
import argparse
from pathlib import Path
from datetime import datetime
from typing import Dict, Any, Optional, List
import pandas as pd
import numpy as np
import joblib

PROJECT_ROOT = Path(__file__).resolve().parent.parent
MODELS_DIR = PROJECT_ROOT / "models" / "rainfall"
ML_RAINFALL_DIR = PROJECT_ROOT / "ml" / "rainfall"
REPORTS_DIR = PROJECT_ROOT / "reports"

sys.path.insert(0, str(Path(__file__).resolve().parent))
from rainfall_model_utils import ExperimentalMeteorologicalRiskBaseline, FEATURE_COLUMNS as DAILY_FEATURE_COLUMNS

SUBDAILY_FEATURE_COLUMNS = [
    "rainfall_1h_mm",
    "rainfall_3h_mm",
    "rainfall_6h_mm",
    "rainfall_24h_mm",
    "rainfall_prev_72h_mm",
    "drainage_capacity_proxy"
]

RISK_THRESHOLDS = {
    "LOW": 0.35,
    "MODERATE": 0.65
}


def get_imd_category(rainfall_mm: float) -> str:
    """Calibrated IMD rainfall intensity classification."""
    if rainfall_mm <= 0.0:
        return "No Rain"
    elif rainfall_mm <= 2.4:
        return "Very Light"
    elif rainfall_mm <= 15.5:
        return "Light"
    elif rainfall_mm <= 64.4:
        return "Moderate"
    elif rainfall_mm <= 115.5:
        return "Heavy"
    elif rainfall_mm <= 204.4:
        return "Very Heavy"
    else:
        return "Extremely Heavy"


def get_risk_level(score: float) -> str:
    """Classifies risk score into categories."""
    if score < 0.20:
        return "Low"
    elif score < 0.45:
        return "Moderate"
    elif score < 0.70:
        return "High"
    else:
        return "Critical"


def load_experimental_model() -> tuple:
    """Loads the trained experimental synthetic model pipeline."""
    candidates = [
        MODELS_DIR / "synthetic_rainfall_model.joblib",
        ML_RAINFALL_DIR / "rainfall_model.joblib"
    ]
    model_path = None
    for p in candidates:
        if p.exists():
            model_path = p
            break

    if model_path is None:
        raise FileNotFoundError(
            f"Experimental model artifact not found in {[str(p) for p in candidates]}. "
            f"Please run `python scripts/train_rainfall_model.py` to train and save the model."
        )

    model = joblib.load(model_path)
    return model, model_path


def load_model_or_baseline() -> tuple:
    """Loads verified supervised model or falls back to transparent heuristic baseline."""
    supervised_path = MODELS_DIR / "best_rainfall_model.joblib"
    baseline_path = MODELS_DIR / "experimental_risk_baseline.joblib"

    if supervised_path.exists():
        model = joblib.load(supervised_path)
        model_type = "Supervised_ML_Model (Trained on verified ground truth)"
        is_supervised = True
    elif baseline_path.exists():
        model = joblib.load(baseline_path)
        model_type = "ExperimentalMeteorologicalRiskBaseline (Unvalidated Heuristic)"
        is_supervised = False
    else:
        model = ExperimentalMeteorologicalRiskBaseline()
        model_type = "ExperimentalMeteorologicalRiskBaseline (Heuristic In-Memory)"
        is_supervised = False

    return model, model_type, is_supervised


def predict_experimental_rainfall(
    rainfall_1h_mm: float,
    rainfall_3h_mm: float,
    rainfall_6h_mm: float,
    rainfall_24h_mm: float,
    rainfall_prev_72h_mm: float,
    drainage_capacity_proxy: float,
    location: str = "Nagpur Locality",
    model_path: Optional[str] = None
) -> Dict[str, Any]:
    """
    Infers waterlogging risk using the trained experimental model on 6 sub-daily features.
    """
    # 1. Input Validation
    features_in = {
        "rainfall_1h_mm": float(rainfall_1h_mm),
        "rainfall_3h_mm": float(rainfall_3h_mm),
        "rainfall_6h_mm": float(rainfall_6h_mm),
        "rainfall_24h_mm": float(rainfall_24h_mm),
        "rainfall_prev_72h_mm": float(rainfall_prev_72h_mm),
        "drainage_capacity_proxy": float(drainage_capacity_proxy)
    }

    warnings = []
    for k, v in features_in.items():
        if np.isnan(v) or np.isinf(v):
            raise ValueError(f"Feature '{k}' cannot be NaN or Inf")
        if v < 0.0:
            raise ValueError(f"Feature '{k}' cannot be negative ({v})")

    # Monotonic accumulation check
    r1, r3, r6, r24 = features_in["rainfall_1h_mm"], features_in["rainfall_3h_mm"], features_in["rainfall_6h_mm"], features_in["rainfall_24h_mm"]
    if r1 > r3 or r3 > r6 or r6 > r24:
        warnings.append(f"Cumulative rainfall window monotonicity violation: 1h({r1}) <= 3h({r3}) <= 6h({r6}) <= 24h({r24})")

    if not (0.0 <= features_in["drainage_capacity_proxy"] <= 1.0):
        warnings.append(f"drainage_capacity_proxy={features_in['drainage_capacity_proxy']} outside typical [0, 1] range")

    # 2. Load Model
    if model_path:
        model = joblib.load(model_path)
        loaded_from = model_path
    else:
        model, loaded_from = load_experimental_model()

    df_X = pd.DataFrame([features_in])[SUBDAILY_FEATURE_COLUMNS]

    # 3. Model Inference
    pred_class = int(model.predict(df_X)[0])
    if hasattr(model, "predict_proba"):
        prob = round(float(model.predict_proba(df_X)[0, 1]), 4)
    else:
        prob = float(pred_class)

    # 4. Risk Categorization
    if prob < RISK_THRESHOLDS["LOW"]:
        risk_category = "LOW"
    elif prob < RISK_THRESHOLDS["MODERATE"]:
        risk_category = "MODERATE"
    else:
        risk_category = "HIGH"

    clf_step = model.named_steps.get("clf", model) if hasattr(model, "named_steps") else model
    model_name = type(clf_step).__name__

    return {
        "location": location,
        "timestamp": datetime.now().isoformat(),
        "predicted_class": pred_class,
        "waterlogging_predicted": bool(pred_class == 1),
        "predicted_probability": prob,
        "risk_category": risk_category,
        "risk_thresholds": RISK_THRESHOLDS,
        "model_name": model_name,
        "model_version": "1.0.0-synthetic",
        "training_data_status": "SYNTHETIC_EXPERIMENTAL",
        "model_source_path": str(loaded_from),
        "input_features": features_in,
        "validation_warnings": warnings,
        "warning": (
            "EXPERIMENTAL MODEL WARNING: This prediction is generated from an experimental model "
            "trained on synthetic demonstration records (waterwatch_ai_nagpur_localities_sample.csv). "
            "It is NOT validated against genuine Nagpur Municipal Corporation (NMC) incident logs "
            "and must NOT be used for civic emergency dispatch without official ground truth."
        )
    }


def predict_rainfall(
    rainfall_mm: Optional[float] = None,
    prev1_mm: float = 0.0,
    prev2_mm: float = 0.0,
    api_7day: Optional[float] = None,
    location: str = "Unknown",
    is_monsoon: Optional[int] = None,
    rainfall_1h_mm: Optional[float] = None,
    rainfall_3h_mm: Optional[float] = None,
    rainfall_6h_mm: Optional[float] = None,
    rainfall_24h_mm: Optional[float] = None,
    rainfall_prev_72h_mm: Optional[float] = None,
    drainage_capacity_proxy: Optional[float] = None
) -> Dict[str, Any]:
    """
    Main entry point for rainfall prediction.
    If sub-daily features are provided, routes to experimental model.
    Otherwise, executes meteorological baseline / daily inference for verified pipeline compatibility.
    """
    # If sub-daily features provided, route to experimental model
    if rainfall_1h_mm is not None:
        r3 = rainfall_3h_mm if rainfall_3h_mm is not None else max(rainfall_1h_mm, 0.0)
        r6 = rainfall_6h_mm if rainfall_6h_mm is not None else max(r3, 0.0)
        r24 = rainfall_24h_mm if rainfall_24h_mm is not None else (rainfall_mm if rainfall_mm is not None else max(r6, 0.0))
        r72 = rainfall_prev_72h_mm if rainfall_prev_72h_mm is not None else 20.0
        dp = drainage_capacity_proxy if drainage_capacity_proxy is not None else 0.50
        return predict_experimental_rainfall(
            rainfall_1h_mm=rainfall_1h_mm,
            rainfall_3h_mm=r3,
            rainfall_6h_mm=r6,
            rainfall_24h_mm=r24,
            rainfall_prev_72h_mm=r72,
            drainage_capacity_proxy=dp,
            location=location
        )

    # Daily rainfall inference (Compatibility Mode)
    if rainfall_mm is None:
        rainfall_mm = 0.0

    now = datetime.now()
    if is_monsoon is None:
        is_monsoon = 1 if now.month in [6, 7, 8, 9] else 0

    total_2day = float(rainfall_mm + prev1_mm)
    total_3day = float(rainfall_mm + prev1_mm + prev2_mm)

    if api_7day is None:
        api_7day = round(0.85 * (0.85 * prev2_mm + prev1_mm), 2)

    trend_ratio = round(rainfall_mm / total_3day, 3) if total_3day > 0 else 1.0

    features = {
        "rainfall_mm": float(rainfall_mm),
        "rainfall_prev1_day_mm": float(prev1_mm),
        "rainfall_prev2_day_mm": float(prev2_mm),
        "rainfall_2day_total_mm": total_2day,
        "rainfall_3day_total_mm": total_3day,
        "api_7day": float(api_7day),
        "rainfall_trend_ratio": trend_ratio,
        "is_monsoon": int(is_monsoon)
    }

    df_X = pd.DataFrame([features])[DAILY_FEATURE_COLUMNS]

    model, model_type, is_supervised = load_model_or_baseline()

    if is_supervised:
        if hasattr(model, "predict_proba"):
            risk_score = round(float(model.predict_proba(df_X)[0, 1]), 4)
        else:
            risk_score = round(float(model.predict(df_X)[0]), 4)
    else:
        risk_score = round(float(model.predict_risk(df_X)[0]), 4)

    imd_cat = get_imd_category(rainfall_mm)
    risk_lvl = get_risk_level(risk_score)

    disclaimer = (
        "Supervised model trained on verified municipal ground-truth."
        if is_supervised else
        "EXPERIMENTAL HEURISTIC: No verified municipal waterlogging labels currently exist in the training dataset. "
        "Scores reflect meteorological runoff hazard derived from IMD precipitation intensity and antecedent soil saturation, "
        "not confirmed local urban drainage capacity."
    )

    return {
        "location": location,
        "timestamp": now.isoformat(),
        "model_architecture": model_type,
        "is_supervised_trained": is_supervised,
        "features": features,
        "imd_category": imd_cat,
        "waterlogging_risk_score": risk_score,
        "risk_level": risk_lvl,
        "scientific_disclaimer": disclaimer
    }


def generate_predictions_report(csv_path: Optional[str] = None) -> Dict[str, Any]:
    """
    Generates actual model predictions for:
    1. A sample of rows from the supplied dataset.
    2. Each supported Nagpur locality represented in the dataset.
    3. Several illustrative example rainfall scenarios.
    Saves outputs to markdown and JSON reports.
    """
    if csv_path is None:
        candidate_csv = PROJECT_ROOT / "waterwatch_ai_nagpur_localities_sample.csv"
        if not candidate_csv.exists():
            candidate_csv = PROJECT_ROOT / "waterwatch_ai_nagpur_localities.csv"
    else:
        candidate_csv = Path(csv_path)

    if not candidate_csv.exists():
        raise FileNotFoundError(f"Dataset not found at {candidate_csv}")

    df = pd.read_csv(candidate_csv)

    # 1. Batch 1: Sample of 10 rows from dataset
    sample_indices = [10, 46, 75, 120, 250, 400, 600, 850, 1100, 1500]
    sample_indices = [i for i in sample_indices if i < len(df)]
    batch_sample_predictions = []

    for idx in sample_indices:
        row = df.iloc[idx]
        pred = predict_experimental_rainfall(
            rainfall_1h_mm=row["rainfall_1h_mm"],
            rainfall_3h_mm=row["rainfall_3h_mm"],
            rainfall_6h_mm=row["rainfall_6h_mm"],
            rainfall_24h_mm=row["rainfall_24h_mm"],
            rainfall_prev_72h_mm=row["rainfall_prev_72h_mm"],
            drainage_capacity_proxy=row["drainage_capacity_proxy"],
            location=f"{row['location_name']} ({row['location_id']})"
        )
        batch_sample_predictions.append({
            "row_index": idx,
            "timestamp": row["timestamp"],
            "location_name": row["location_name"],
            "location_id": row["location_id"],
            "rainfall_1h_mm": float(row["rainfall_1h_mm"]),
            "rainfall_24h_mm": float(row["rainfall_24h_mm"]),
            "drainage_capacity_proxy": float(row["drainage_capacity_proxy"]),
            "ground_truth_label": int(row["waterlogging_observed"]),
            "ground_truth_severity": str(row["severity"]),
            "predicted_class": pred["predicted_class"],
            "predicted_probability": pred["predicted_probability"],
            "risk_category": pred["risk_category"]
        })

    # 2. Batch 2: Each supported Nagpur Locality
    locality_stats = df.groupby(["location_id", "location_name"])["drainage_capacity_proxy"].mean().reset_index()
    batch_locality_predictions = []

    # Test each locality under standard moderate monsoon rain (1h=15.0mm, 3h=30.0mm, 6h=45.0mm, 24h=65.0mm, 72h=90.0mm)
    for _, loc in locality_stats.iterrows():
        proxy_val = round(float(loc["drainage_capacity_proxy"]), 3)
        pred = predict_experimental_rainfall(
            rainfall_1h_mm=18.0,
            rainfall_3h_mm=32.0,
            rainfall_6h_mm=48.0,
            rainfall_24h_mm=70.0,
            rainfall_prev_72h_mm=95.0,
            drainage_capacity_proxy=proxy_val,
            location=f"{loc['location_name']} ({loc['location_id']})"
        )
        batch_locality_predictions.append({
            "location_id": loc["location_id"],
            "location_name": loc["location_name"],
            "drainage_capacity_proxy": proxy_val,
            "test_rainfall_condition": "Moderate Monsoon (1h=18mm, 24h=70mm)",
            "predicted_class": pred["predicted_class"],
            "predicted_probability": pred["predicted_probability"],
            "risk_category": pred["risk_category"]
        })

    # 3. Batch 3: Illustrative Rainfall Scenarios
    scenarios = [
        {
            "scenario_name": "Dry Weather / Negligible Rain",
            "rainfall_1h_mm": 0.0,
            "rainfall_3h_mm": 1.5,
            "rainfall_6h_mm": 3.0,
            "rainfall_24h_mm": 5.0,
            "rainfall_prev_72h_mm": 15.0,
            "drainage_capacity_proxy": 0.75,
            "description": "Clear dry day with functioning road drains"
        },
        {
            "scenario_name": "Typical Monsoon Rainfall",
            "rainfall_1h_mm": 12.0,
            "rainfall_3h_mm": 24.0,
            "rainfall_6h_mm": 38.0,
            "rainfall_24h_mm": 52.0,
            "rainfall_prev_72h_mm": 75.0,
            "drainage_capacity_proxy": 0.58,
            "description": "Standard monsoon shower in central Nagpur"
        },
        {
            "scenario_name": "Heavy Downpour / Saturated Soil",
            "rainfall_1h_mm": 32.0,
            "rainfall_3h_mm": 54.0,
            "rainfall_6h_mm": 72.0,
            "rainfall_24h_mm": 98.0,
            "rainfall_prev_72h_mm": 140.0,
            "drainage_capacity_proxy": 0.42,
            "description": "Intense afternoon thunderstorm on pre-saturated ground"
        },
        {
            "scenario_name": "Severe Cloudburst & Obstructed Drain",
            "rainfall_1h_mm": 58.0,
            "rainfall_3h_mm": 78.0,
            "rainfall_6h_mm": 98.0,
            "rainfall_24h_mm": 135.0,
            "rainfall_prev_72h_mm": 180.0,
            "drainage_capacity_proxy": 0.20,
            "description": "Extreme precipitation event with severely blocked storm drains"
        }
    ]

    batch_scenario_predictions = []
    for sc in scenarios:
        pred = predict_experimental_rainfall(
            rainfall_1h_mm=sc["rainfall_1h_mm"],
            rainfall_3h_mm=sc["rainfall_3h_mm"],
            rainfall_6h_mm=sc["rainfall_6h_mm"],
            rainfall_24h_mm=sc["rainfall_24h_mm"],
            rainfall_prev_72h_mm=sc["rainfall_prev_72h_mm"],
            drainage_capacity_proxy=sc["drainage_capacity_proxy"],
            location="Nagpur (Illustrative)"
        )
        batch_scenario_predictions.append({
            "scenario_name": sc["scenario_name"],
            "description": sc["description"],
            "inputs": {
                "rainfall_1h_mm": sc["rainfall_1h_mm"],
                "rainfall_3h_mm": sc["rainfall_3h_mm"],
                "rainfall_6h_mm": sc["rainfall_6h_mm"],
                "rainfall_24h_mm": sc["rainfall_24h_mm"],
                "rainfall_prev_72h_mm": sc["rainfall_prev_72h_mm"],
                "drainage_capacity_proxy": sc["drainage_capacity_proxy"]
            },
            "predicted_class": pred["predicted_class"],
            "predicted_probability": pred["predicted_probability"],
            "risk_category": pred["risk_category"]
        })

    report_data = {
        "dataset_source": candidate_csv.name,
        "generation_timestamp": datetime.now().isoformat(),
        "training_data_status": "SYNTHETIC_EXPERIMENTAL",
        "model_name": "LogisticRegression (StandardScaler pipeline)",
        "sample_rows_predictions": batch_sample_predictions,
        "locality_predictions": batch_locality_predictions,
        "scenario_predictions": batch_scenario_predictions
    }

    # Save JSON report
    REPORTS_DIR.mkdir(parents=True, exist_ok=True)
    json_path = REPORTS_DIR / "sample_predictions.json"
    with open(json_path, "w", encoding="utf-8") as f:
        json.dump(report_data, f, indent=2)

    # Save Markdown report
    md_lines = [
        "# WaterWatch AI — Model Predictions Demonstration Report",
        "",
        f"**Dataset Source**: `{candidate_csv.name}`  ",
        f"**Model Status**: `SYNTHETIC_EXPERIMENTAL`  ",
        f"**Timestamp**: `{report_data['generation_timestamp']}`  ",
        "",
        "> [!WARNING]",
        "> **Illustrative Demonstration Notice**: All predictions below were generated by the experimental model "
        "trained on synthetic demonstration records. They are illustrative examples and NOT real-time weather forecasts "
        "or official municipal emergency alerts.",
        "",
        "---",
        "",
        "## 1. Actual Predictions on Sample Rows from Supplied Dataset",
        "",
        "| Row | Timestamp | Locality | 1h (mm) | 24h (mm) | Drainage Proxy | Ground Truth | Predicted Class | Prob | Risk Category |",
        "| :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- |"
    ]

    for p in batch_sample_predictions:
        md_lines.append(
            f"| `{p['row_index']}` | {p['timestamp'][:16]} | {p['location_name']} | "
            f"`{p['rainfall_1h_mm']}` | `{p['rainfall_24h_mm']}` | `{p['drainage_capacity_proxy']}` | "
            f"`{p['ground_truth_label']}` ({p['ground_truth_severity']}) | **{p['predicted_class']}** | "
            f"`{p['predicted_probability']:.4f}` | **{p['risk_category']}** |"
        )

    md_lines.extend([
        "",
        "---",
        "",
        "## 2. Predictions Summarized by Nagpur Locality",
        "",
        "Evaluated under a uniform moderate monsoon rainfall event (1h=18mm, 24h=70mm) using each locality's dataset drainage proxy:",
        "",
        "| Locality ID | Locality Name | Drainage Proxy | Predicted Class | Flood Probability | Risk Category |",
        "| :--- | :--- | :--- | :--- | :--- | :--- |"
    ])

    for p in batch_locality_predictions:
        md_lines.append(
            f"| `{p['location_id']}` | **{p['location_name']}** | `{p['drainage_capacity_proxy']}` | "
            f"**{p['predicted_class']}** | `{p['predicted_probability']:.4f}` | **{p['risk_category']}** |"
        )

    md_lines.extend([
        "",
        "---",
        "",
        "## 3. Predictions on Illustrative Weather Scenarios",
        "",
        "| Scenario Name | Description | 1h / 24h Rain | Drainage Proxy | Predicted Class | Probability | Risk Category |",
        "| :--- | :--- | :--- | :--- | :--- | :--- | :--- |"
    ])

    for p in batch_scenario_predictions:
        inp = p["inputs"]
        md_lines.append(
            f"| **{p['scenario_name']}** | {p['description']} | `{inp['rainfall_1h_mm']}` / `{inp['rainfall_24h_mm']} mm` | "
            f"`{inp['drainage_capacity_proxy']}` | **{p['predicted_class']}** | `{p['predicted_probability']:.4f}` | **{p['risk_category']}** |"
        )

    md_path = REPORTS_DIR / "sample_predictions_report.md"
    with open(md_path, "w", encoding="utf-8") as f:
        f.write("\n".join(md_lines))

    print(f"Generated sample predictions report saved to {md_path} and {json_path}")
    return report_data


def main():
    parser = argparse.ArgumentParser(description="WaterWatch Rainfall Prediction Inference Engine")
    parser.add_argument("--generate-samples", action="store_true", help="Generate full batch sample prediction report")
    parser.add_argument("--rainfall_mm", type=float, default=None, help="Current 24-hr observed rainfall in mm")
    parser.add_argument("--prev1_mm", type=float, default=0.0, help="Previous day rainfall (lag-1) in mm")
    parser.add_argument("--prev2_mm", type=float, default=0.0, help="2 days prior rainfall (lag-2) in mm")
    parser.add_argument("--api_7day", type=float, default=None, help="7-day Antecedent Precipitation Index")
    parser.add_argument("--location", type=str, default="Nagpur", help="Location or locality name")
    parser.add_argument("--is_monsoon", type=int, default=None, choices=[0, 1], help="Monsoon flag (0 or 1)")
    # Sub-daily telemetry arguments for experimental model
    parser.add_argument("--rain-1h", type=float, default=None, help="1-hour rainfall in mm")
    parser.add_argument("--rain-3h", type=float, default=None, help="3-hour rainfall in mm")
    parser.add_argument("--rain-6h", type=float, default=None, help="6-hour rainfall in mm")
    parser.add_argument("--rain-24h", type=float, default=None, help="24-hour rainfall in mm")
    parser.add_argument("--rain-72h", type=float, default=None, help="Previous 72-hour rainfall in mm")
    parser.add_argument("--drainage-proxy", type=float, default=None, help="Drainage capacity proxy [0.0, 1.0]")
    parser.add_argument("--json", action="store_true", help="Output pure JSON")

    args = parser.parse_args()

    if args.generate_samples:
        report = generate_predictions_report()
        print("\n=== SAMPLE PREDICTIONS SUMMARY ===")
        print(f"Rows evaluated: {len(report['sample_rows_predictions'])}")
        print(f"Localities evaluated: {len(report['locality_predictions'])}")
        print(f"Scenarios evaluated: {len(report['scenario_predictions'])}")
        return

    # Check if sub-daily args provided
    if args.rain_1h is not None:
        result = predict_rainfall(
            rainfall_1h_mm=args.rain_1h,
            rainfall_3h_mm=args.rain_3h,
            rainfall_6h_mm=args.rain_6h,
            rainfall_24h_mm=args.rain_24h,
            rainfall_prev_72h_mm=args.rain_72h,
            drainage_capacity_proxy=args.drainage_proxy,
            location=args.location
        )
    elif args.rainfall_mm is not None:
        result = predict_rainfall(
            rainfall_mm=args.rainfall_mm,
            prev1_mm=args.prev1_mm,
            prev2_mm=args.prev2_mm,
            api_7day=args.api_7day,
            location=args.location,
            is_monsoon=args.is_monsoon
        )
    else:
        # Default demo
        print("No specific rainfall arguments supplied. Generating demonstration batch report...")
        report = generate_predictions_report()
        return

    if args.json:
        print(json.dumps(result, indent=2))
    else:
        print("\n" + "=" * 65)
        print("   WATERWATCH AI — RAINFALL RISK INFERENCE")
        print("=" * 65)
        print(f"  Location              : {result['location']}")
        if "model_name" in result:
            print(f"  Model Engine          : {result['model_name']} ({result['model_version']})")
            print(f"  Training Status       : {result['training_data_status']}")
            print(f"  Waterlogging Predicted: {result['waterlogging_predicted']} (Class {result['predicted_class']})")
            print(f"  Predicted Probability : {result['predicted_probability']:.4f}")
            print(f"  Risk Category         : {result['risk_category']}")
            print(f"  1h / 24h Rainfall     : {result['input_features']['rainfall_1h_mm']} mm / {result['input_features']['rainfall_24h_mm']} mm")
            print(f"  Drainage Proxy        : {result['input_features']['drainage_capacity_proxy']}")
            print("=" * 65)
            print(f"\n  [WARNING] {result['warning']}\n")
        else:
            print(f"  Model Engine          : {result['model_architecture']}")
            print(f"  Supervised Grounded   : {result['is_supervised_trained']}")
            print(f"  Current Rainfall      : {result['features']['rainfall_mm']} mm ({result['imd_category']})")
            print(f"  Antecedent 7-day API  : {result['features']['api_7day']} mm")
            print(f"  Waterlogging Risk     : {result['waterlogging_risk_score']:.4f}  [{result['risk_level'].upper()}]")
            print("=" * 65)
            print(f"\n  [NOTE] {result['scientific_disclaimer']}\n")


if __name__ == "__main__":
    main()
