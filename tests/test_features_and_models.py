"""
Unit and Integration Tests for Rainfall Feature Engineering & Model Pipeline
Tests feature generation, risk score bounds, hydrological monotonicity, and model serialization.
"""

import os
import sys
import json
from pathlib import Path
import pandas as pd
import numpy as np
import joblib
import pytest

PROJECT_ROOT = Path(__file__).resolve().parent.parent
PROCESSED_DIR = PROJECT_ROOT / "data" / "processed"
MODELS_DIR = PROJECT_ROOT / "models" / "rainfall"
MANIFESTS_DIR = PROJECT_ROOT / "data" / "manifests"

sys.path.insert(0, str(PROJECT_ROOT / "scripts"))
from rainfall_model_utils import ExperimentalMeteorologicalRiskBaseline, FEATURE_COLUMNS


def test_feature_dataset_and_columns():
    feat_file = PROCESSED_DIR / "rainfall_daily_features.csv"
    assert feat_file.exists(), f"Missing feature dataset: {feat_file}"
    df = pd.read_csv(feat_file)

    expected_cols = [
        "rainfall_mm",
        "rainfall_prev1_day_mm",
        "rainfall_prev2_day_mm",
        "rainfall_2day_total_mm",
        "rainfall_3day_total_mm",
        "api_7day",
        "rainfall_trend_ratio",
        "imd_category",
        "experimental_risk_score",
        "experimental_risk_level"
    ]
    for col in expected_cols:
        assert col in df.columns, f"Expected column {col} missing from daily features"


def test_risk_score_bounds_and_distribution():
    feat_file = PROCESSED_DIR / "rainfall_daily_features.csv"
    df = pd.read_csv(feat_file)

    scores = df["experimental_risk_score"].dropna()
    assert (scores >= 0.0).all(), "Risk score contains values < 0.0"
    assert (scores <= 1.0).all(), "Risk score contains values > 1.0"


def test_hydrological_monotonicity():
    """Verify that heavier precipitation yields systematically higher risk scores."""
    feat_file = PROCESSED_DIR / "rainfall_daily_features.csv"
    df = pd.read_csv(feat_file)

    light_mean_risk = df[df["rainfall_mm"] < 10.0]["experimental_risk_score"].mean()
    heavy_mean_risk = df[df["rainfall_mm"] > 70.0]["experimental_risk_score"].mean()

    assert heavy_mean_risk > light_mean_risk, (
        f"Monotonicity violation: heavy mean risk ({heavy_mean_risk:.3f}) "
        f"not greater than light mean risk ({light_mean_risk:.3f})"
    )


def test_event_schema_json_validity():
    schema_file = MANIFESTS_DIR / "waterlogging_event_schema.json"
    assert schema_file.exists(), f"Missing schema file: {schema_file}"
    with open(schema_file, "r", encoding="utf-8") as f:
        schema = json.load(f)

    assert "properties" in schema
    assert "event_id" in schema["properties"]
    assert "timestamp_start" in schema["properties"]
    assert "latitude" in schema["properties"]
    assert "longitude" in schema["properties"]
    assert "waterlogged_label" in schema["properties"]


def test_baseline_model_artifact_and_predict():
    model_file = MODELS_DIR / "experimental_risk_baseline.joblib"
    assert model_file.exists(), f"Missing baseline artifact: {model_file}"

    model = joblib.load(model_file)
    sample_data = pd.DataFrame([{
        "rainfall_mm": 85.0,
        "rainfall_prev1_day_mm": 40.0,
        "rainfall_prev2_day_mm": 20.0,
        "rainfall_2day_total_mm": 125.0,
        "rainfall_3day_total_mm": 145.0,
        "api_7day": 95.0,
        "rainfall_trend_ratio": 0.58,
        "is_monsoon": 1
    }])

    risk = model.predict_risk(sample_data)[0]
    assert 0.0 <= risk <= 1.0, f"Predicted risk out of bounds: {risk}"
    assert risk >= 0.50, f"Expected elevated risk for 85mm rainfall, got {risk}"
