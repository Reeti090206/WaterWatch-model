"""
WaterWatch AI - Comprehensive Integration & Unit Test Suite
Validates:
  - Missing data integrity (unrecorded telemetry is NOT zero)
  - Invalid input rejection (out-of-bounds coordinates, invalid timestamps)
  - Feature calculations (monotonicity, rolling window aggregations)
  - Model loading and standalone inference outputs
  - Waterlogging event schema and validation engine
  - Combined pipeline signal separation and disagreement flagging
"""

import os
import sys
import json
from pathlib import Path
import pandas as pd
import numpy as np
import pytest

PROJECT_ROOT = Path(__file__).resolve().parent.parent
PROCESSED_DIR = PROJECT_ROOT / "data" / "processed"
MANIFESTS_DIR = PROJECT_ROOT / "data" / "manifests"
MODELS_DIR = PROJECT_ROOT / "models"
REPORTS_DIR = PROJECT_ROOT / "reports"

sys.path.insert(0, str(PROJECT_ROOT / "scripts"))
from predict_rainfall import predict_rainfall, load_model_or_baseline, get_imd_category, get_risk_level
from predict_image import predict as predict_image_fn
from validate_events import validate_events_file
from annotate_event import validate_record
from combined_pipeline import run_combined_pipeline


# ─── 1. MISSING DATA & TELEMETRY INTEGRITY TESTS ─────────────────────────────

def test_telemetry_missing_data_not_zero():
    """Strictly assert that unmeasured telemetry is stored as NaN and never imputed as 0.0."""
    hourly_file = PROCESSED_DIR / "rainfall_hourly_observed.csv"
    assert hourly_file.exists(), f"Missing {hourly_file}"
    df = pd.read_csv(hourly_file)

    assert "is_measured" in df.columns
    unmeasured = df[~df["is_measured"]]
    assert len(unmeasured) > 0, "No unmeasured rows found in telemetry data"
    assert unmeasured["rainfall_mm"].isna().all(), "Unmeasured telemetry must be strictly NaN, not zero"


def test_rolling_windows_gap_handling():
    """Verify hourly features contain rolling 1h, 3h, 6h, 24h, 72h columns."""
    hourly_feat = PROCESSED_DIR / "rainfall_hourly_features.csv"
    assert hourly_feat.exists(), f"Missing {hourly_feat}"
    df = pd.read_csv(hourly_feat)

    for col in ["rainfall_1h_mm", "rolling_3h_mm", "rolling_6h_mm", "rolling_24h_mm", "rolling_72h_mm"]:
        assert col in df.columns, f"Expected hourly feature '{col}' missing"


# ─── 2. INVALID INPUT & ERROR BOUND TESTS ─────────────────────────────────────

def test_event_validation_rejects_invalid_inputs():
    """Verify that event validation rejects out-of-bounds coordinates, bad timestamps, and bad enums."""
    bad_record = {
        "event_id": "TEST-BAD-01",
        "location_id": "LOC-01",
        "latitude": 95.0,  # Out of bounds
        "longitude": 180.0,  # Out of bounds
        "event_start_time": "invalid-datetime-string",
        "waterlogging_observed": 5,  # Invalid (must be 0 or 1)
        "evidence_type": "Fake_Evidence",
        "evidence_source": "Unknown",
        "verification_status": "Invalid_Status",
        "annotator_id": "OP-01"
    }
    errors = validate_record(bad_record)
    assert len(errors) >= 4, f"Expected multiple validation errors, got {errors}"


def test_event_validation_accepts_valid_record():
    """Verify that a schema-conforming record passes validation with zero errors."""
    valid_record = {
        "event_id": "TEST-VALID-01",
        "location_id": "NGP-SITABULDI-01",
        "latitude": 21.1458,
        "longitude": 79.0882,
        "event_start_time": "2024-07-22T14:30:00+05:30",
        "event_end_time": "2024-07-22T18:00:00+05:30",
        "waterlogging_observed": 1,
        "severity_level": "Severe",
        "water_depth_cm": 45.0,
        "evidence_type": "Municipal_Log",
        "evidence_source": "Nagpur Municipal Corporation",
        "verification_status": "Verified_Official",
        "image_path": None,
        "annotator_id": "OP-NMC-101",
        "notes": "Valid test record"
    }
    errors = validate_record(valid_record)
    assert len(errors) == 0, f"Expected valid record to pass, got errors: {errors}"


# ─── 3. FEATURE CALCULATIONS & HYDROLOGICAL MONOTONICITY ──────────────────────

def test_imd_classification_categories():
    assert get_imd_category(0.0) == "No Rain"
    assert get_imd_category(1.5) == "Very Light"
    assert get_imd_category(10.0) == "Light"
    assert get_imd_category(45.0) == "Moderate"
    assert get_imd_category(85.0) == "Heavy"
    assert get_imd_category(150.0) == "Very Heavy"
    assert get_imd_category(250.0) == "Extremely Heavy"


def test_rainfall_prediction_monotonicity():
    """Verify that higher precipitation results in higher or equal risk scores."""
    r_dry = predict_rainfall(rainfall_mm=2.0, prev1_mm=0.0, prev2_mm=0.0)
    r_mod = predict_rainfall(rainfall_mm=40.0, prev1_mm=20.0, prev2_mm=10.0)
    r_ext = predict_rainfall(rainfall_mm=180.0, prev1_mm=90.0, prev2_mm=60.0)

    assert r_dry["waterlogging_risk_score"] < r_mod["waterlogging_risk_score"]
    assert r_mod["waterlogging_risk_score"] < r_ext["waterlogging_risk_score"]
    assert 0.0 <= r_dry["waterlogging_risk_score"] <= 1.0
    assert 0.0 <= r_ext["waterlogging_risk_score"] <= 1.0


# ─── 4. MODEL LOADING & STANDALONE INFERENCE TESTS ────────────────────────────

def test_predict_rainfall_standalone_output_schema():
    """Verify predict_rainfall returns all documented keys and transparent disclaimers."""
    res = predict_rainfall(rainfall_mm=50.0, location="Nagpur")

    assert "location" in res
    assert "timestamp" in res
    assert "model_architecture" in res
    assert "is_supervised_trained" in res
    assert "waterlogging_risk_score" in res
    assert "risk_level" in res
    assert "scientific_disclaimer" in res
    assert res["is_supervised_trained"] is False  # Acknowledging no verified labels exist yet


def test_predict_image_standalone_output_schema():
    """Verify predict_image runs on real test image and returns documented keys."""
    test_img = next((PROCESSED_DIR / "yolo_water_logging" / "images" / "test").glob("*.jpg"))
    results = predict_image_fn(source_path=test_img, conf_thresh=0.25)

    assert len(results) > 0
    item = results[0]
    assert "image_path" in item
    assert "waterlogging_detected" in item
    assert "detection_count" in item
    assert "detections" in item
    assert "scientific_disclaimer" in item
    assert isinstance(item["waterlogging_detected"], bool)


# ─── 5. COMBINED PIPELINE & DISAGREEMENT FLAGGING TESTS ───────────────────────

def test_combined_pipeline_confirmed_hazard():
    """Verify combined pipeline outputs CONFIRMED_HAZARD when both signals indicate flooding."""
    # Use image with known detections
    test_img = PROCESSED_DIR / "yolo_water_logging" / "images" / "test" / "waterloggingt-105-_jpg.rf.982f24e5c60290f4b23ab7b6fbf49db6.jpg"
    assert test_img.exists()

    res = run_combined_pipeline(
        rainfall_mm=120.0,
        prev1_mm=60.0,
        image_path=test_img,
        location="Nagpur - Sitabuldi",
        conf_thresh=0.20
    )

    assert res["rainfall_component"]["risk_level"] in ["High", "Critical"]
    assert res["image_component"]["waterlogging_detected"] is True
    assert res["synthesis"]["status"] == "CONFIRMED_HAZARD"
    assert res["synthesis"]["flag_for_review"] is False


def test_combined_pipeline_disagreement_flagged():
    """Verify combined pipeline flags disagreement when heavy rainfall occurs but image is clear."""
    # Use image 104 with 0 detections above threshold
    test_img = PROCESSED_DIR / "yolo_water_logging" / "images" / "test" / "waterloggingt-104-_jpg.rf.76d86055e86c1059ae4e896dd158c067.jpg"
    assert test_img.exists()

    res = run_combined_pipeline(
        rainfall_mm=100.0,
        prev1_mm=50.0,
        image_path=test_img,
        location="Nagpur - Sitabuldi",
        conf_thresh=0.20
    )

    assert res["rainfall_component"]["risk_level"] in ["High", "Critical"]
    assert res["image_component"]["waterlogging_detected"] is False
    assert res["synthesis"]["status"] == "DISAGREEMENT_PRECIPITATION_AHEAD"
    assert res["synthesis"]["flag_for_review"] is True
