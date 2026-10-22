"""
WaterWatch AI - Standalone Rainfall Prediction Engine
Provides validated, reproducible risk inference using the fitted rainfall model.
Includes strict feature verification, boundary checks, and transparent
experimental synthetic-data disclaimers.
"""

import os
import sys
import json
from pathlib import Path
from typing import Dict, Any, Union, List, Optional, Tuple
import pandas as pd
import numpy as np
import joblib

FEATURE_COLUMNS = [
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


class ModelLoadError(Exception):
    """Raised when the trained model artifact cannot be found or loaded."""
    pass


class FeatureValidationError(ValueError):
    """Raised when input features fail strict schema or range validation."""
    pass


def load_model_and_metadata(model_path: Optional[Union[str, Path]] = None) -> tuple:
    """
    Loads the trained pipeline and associated metadata.
    Raises ModelLoadError if artifacts are missing (strictly avoiding silent hardcoded fallbacks).
    """
    project_root = Path(__file__).resolve().parent.parent.parent
    if model_path is None:
        candidate_paths = [
            project_root / "ml" / "rainfall" / "rainfall_model.joblib",
            project_root / "models" / "rainfall" / "synthetic_rainfall_model.joblib"
        ]
        target_path = None
        for p in candidate_paths:
            if p.exists():
                target_path = p
                break
        if target_path is None:
            raise ModelLoadError(
                f"Model file not found. Candidates searched: {[str(p) for p in candidate_paths]}. "
                f"Please run `python ml/rainfall/train_rainfall_model.py` to train and save the model."
            )
    else:
        target_path = Path(model_path)
        if not target_path.exists():
            raise ModelLoadError(f"Specified model path does not exist: {target_path}")

    try:
        pipeline = joblib.load(target_path)
    except Exception as e:
        raise ModelLoadError(f"Failed to deserialize model at {target_path}: {str(e)}")

    # Load metadata if present
    meta_path = target_path.parent / "model_metadata.json"
    metadata = {}
    if meta_path.exists():
        try:
            with open(meta_path, "r", encoding="utf-8") as f:
                metadata = json.load(f)
        except Exception:
            metadata = {}

    return pipeline, metadata, target_path


def validate_input_features(features: Dict[str, Any], strict_monotonic: bool = False) -> Tuple[Dict[str, float], List[str]]:
    """
    Validates input feature types, completeness, and hydrological boundaries.
    """
    warnings = []
    cleaned = {}

    # Check required fields
    missing = [f for f in FEATURE_COLUMNS if f not in features]
    if missing:
        raise FeatureValidationError(f"Missing required rainfall features: {missing}")

    for f in FEATURE_COLUMNS:
        val = features[f]
        try:
            val_f = float(val)
        except (ValueError, TypeError):
            raise FeatureValidationError(f"Feature '{f}' must be numeric; got {val} ({type(val).__name__})")

        if np.isnan(val_f) or np.isinf(val_f):
            raise FeatureValidationError(f"Feature '{f}' cannot be NaN or Inf")

        if val_f < 0.0:
            raise FeatureValidationError(f"Rainfall and drainage features cannot be negative; got {f}={val_f}")

        cleaned[f] = val_f

    # Validate drainage proxy range
    dp = cleaned["drainage_capacity_proxy"]
    if dp > 1.0:
        warnings.append(f"drainage_capacity_proxy={dp} exceeds typical [0.0, 1.0] scale; clamping impact")

    # Validate monotonic window accumulation
    r1, r3, r6, r24 = cleaned["rainfall_1h_mm"], cleaned["rainfall_3h_mm"], cleaned["rainfall_6h_mm"], cleaned["rainfall_24h_mm"]
    if r1 > r3 or r3 > r6 or r6 > r24:
        msg = f"Inconsistent cumulative rainfall windows: 1h({r1}) <= 3h({r3}) <= 6h({r6}) <= 24h({r24}) violated."
        if strict_monotonic:
            raise FeatureValidationError(msg)
        else:
            warnings.append(msg)

    return cleaned, warnings


def predict_waterlogging(
    features: Dict[str, Any],
    model_path: Optional[Union[str, Path]] = None,
    strict_monotonic: bool = False
) -> Dict[str, Any]:
    """
    Predicts waterlogging occurrence and synthetic risk score for given rainfall conditions.
    
    Args:
        features: Dictionary containing rainfall windows and drainage proxy.
        model_path: Optional path to joblib model file.
        strict_monotonic: If True, raises exception on 1h > 3h > 6h > 24h violations.
        
    Returns:
        Structured prediction result dictionary.
    """
    pipeline, metadata, loaded_path = load_model_and_metadata(model_path)
    cleaned_features, warnings = validate_input_features(features, strict_monotonic=strict_monotonic)

    # Format into DataFrame with exact feature order
    X_df = pd.DataFrame([cleaned_features])[FEATURE_COLUMNS]

    # Predict
    pred_class = int(pipeline.predict(X_df)[0])
    if hasattr(pipeline, "predict_proba"):
        probs = pipeline.predict_proba(X_df)[0]
        model_score = round(float(probs[1]), 4)
    else:
        model_score = float(pred_class)

    # Determine risk category
    if model_score < RISK_THRESHOLDS["LOW"]:
        risk_category = "LOW"
    elif model_score < RISK_THRESHOLDS["MODERATE"]:
        risk_category = "MODERATE"
    else:
        risk_category = "HIGH"

    model_name = metadata.get("model_name", type(pipeline.named_steps.get("clf", pipeline)).__name__)
    model_version = metadata.get("model_version", "1.0.0-synthetic")

    return {
        "predicted_class": pred_class,
        "waterlogging_predicted": bool(pred_class == 1),
        "model_score": model_score,
        "risk_category": risk_category,
        "risk_thresholds": RISK_THRESHOLDS,
        "model_name": model_name,
        "model_version": model_version,
        "model_source_path": str(loaded_path),
        "training_data_status": "SYNTHETIC_EXPERIMENTAL",
        "validation_warnings": warnings,
        "input_features": cleaned_features,
        "scientific_disclaimer": (
            "Experimental prediction derived from synthetic demonstration data. "
            "The model score indicates synthetic pattern activation, NOT a calibrated real-world flooding probability. "
            "Do NOT use for official municipal emergency response without ground-truth NMC calibration."
        )
    }


def main():
    import argparse
    parser = argparse.ArgumentParser(description="WaterWatch AI Standalone Rainfall Predictor (CLI Demo)")
    parser.add_argument("--rain-1h", type=float, default=25.0, help="1-hour rainfall in mm")
    parser.add_argument("--rain-3h", type=float, default=45.0, help="3-hour rainfall in mm")
    parser.add_argument("--rain-6h", type=float, default=65.0, help="6-hour rainfall in mm")
    parser.add_argument("--rain-24h", type=float, default=95.0, help="24-hour rainfall in mm")
    parser.add_argument("--rain-72h", type=float, default=120.0, help="Previous 72-hour rainfall in mm")
    parser.add_argument("--drainage-proxy", type=float, default=0.35, help="Drainage capacity proxy [0.0, 1.0]")
    parser.add_argument("--model-path", type=str, default=None, help="Custom path to model .joblib")
    args = parser.parse_args()

    sample_input = {
        "rainfall_1h_mm": args.rain_1h,
        "rainfall_3h_mm": args.rain_3h,
        "rainfall_6h_mm": args.rain_6h,
        "rainfall_24h_mm": args.rain_24h,
        "rainfall_prev_72h_mm": args.rain_72h,
        "drainage_capacity_proxy": args.drainage_proxy
    }

    print("\n" + "=" * 65)
    print("WATERWATCH AI — EXPERIMENTAL RAINFALL RISK INFERENCE DEMO")
    print("=" * 65)
    print("Input Telemetry:")
    for k, v in sample_input.items():
        print(f"  - {k}: {v}")

    try:
        result = predict_waterlogging(sample_input, model_path=args.model_path)
        print("\nPrediction Results:")
        print(f"  - Waterlogging Predicted: {result['waterlogging_predicted']} (Class {result['predicted_class']})")
        print(f"  - Experimental Model Score: {result['model_score']:.4f}")
        print(f"  - Risk Category: {result['risk_category']}")
        print(f"  - Model: {result['model_name']} ({result['model_version']})")
        print(f"  - Data Status: {result['training_data_status']}")
        if result["validation_warnings"]:
            print(f"  - Warnings: {result['validation_warnings']}")
        print(f"\n[DISCLAIMER]: {result['scientific_disclaimer']}")
    except Exception as e:
        print(f"\n[ERROR]: Prediction failed: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
