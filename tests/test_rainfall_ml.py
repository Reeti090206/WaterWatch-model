"""
Unit and Integration Tests for WaterWatch AI Machine Learning Pipeline
Covers:
- Dataset validation, schema integrity, missing/malformed fields, invalid targets
- Non-negative rainfall constraints & window monotonicity violations
- Supervised model training, temporal splitting, and metric computation
- Model serialization & reload fidelity
- Inference input validation, range checks, and output schema
- Missing model file error handling (anti-fallback verification)
- Image inference graceful failure handling when weights/data are missing
"""

import os
import sys
import tempfile
import json
from pathlib import Path
import pytest
import pandas as pd
import numpy as np
import joblib

PROJECT_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

from ml.rainfall.validate_dataset import validate_dataset, DatasetValidationError
from ml.rainfall.train_rainfall_model import train_and_evaluate, FEATURE_COLUMNS
from ml.rainfall.predict_rainfall import (
    predict_waterlogging,
    validate_input_features,
    load_model_and_metadata,
    ModelLoadError,
    FeatureValidationError
)


@pytest.fixture
def valid_synthetic_df():
    """Returns a clean, valid synthetic DataFrame with 20 rows."""
    return pd.DataFrame({
        "timestamp": [f"2025-06-01 {h:02d}:00:00" for h in range(20)],
        "location_id": [f"LOC_{i%4}" for i in range(20)],
        "location_name": [f"Locality {i%4}" for i in range(20)],
        "rainfall_1h_mm": [float(i * 1.5) for i in range(20)],
        "rainfall_3h_mm": [float(i * 2.5 + 2.0) for i in range(20)],
        "rainfall_6h_mm": [float(i * 3.5 + 5.0) for i in range(20)],
        "rainfall_24h_mm": [float(i * 4.5 + 10.0) for i in range(20)],
        "rainfall_prev_72h_mm": [float(i * 5.0 + 20.0) for i in range(20)],
        "drainage_capacity_proxy": [0.4 + (i % 5) * 0.1 for i in range(20)],
        "waterlogging_observed": [1 if i % 3 == 0 else 0 for i in range(20)],
        "severity": ["moderate" if i % 3 == 0 else "none" for i in range(20)]
    })


# 1. Dataset Loading and Schema Validation Tests
def test_validation_on_clean_data(valid_synthetic_df):
    findings = validate_dataset(valid_synthetic_df, generate_reports=False)
    assert findings["is_valid"] is True
    assert findings["total_records"] == 20
    assert len(findings["critical_errors"]) == 0
    assert findings["consistency"]["monotonic_integrity_pass"] is True


def test_validation_detects_missing_columns(valid_synthetic_df):
    broken_df = valid_synthetic_df.drop(columns=["rainfall_24h_mm", "drainage_capacity_proxy"])
    findings = validate_dataset(broken_df, generate_reports=False)
    assert findings["is_valid"] is False
    assert any("Missing required columns" in err for err in findings["critical_errors"])


def test_validation_detects_invalid_target_labels(valid_synthetic_df):
    corrupt_df = valid_synthetic_df.copy()
    corrupt_df.loc[0, "waterlogging_observed"] = 5  # Non-binary target
    findings = validate_dataset(corrupt_df, generate_reports=False)
    assert findings["is_valid"] is False
    assert any("must only contain 0 and 1" in err for err in findings["critical_errors"])


def test_validation_detects_negative_rainfall(valid_synthetic_df):
    neg_df = valid_synthetic_df.copy()
    neg_df.loc[2, "rainfall_1h_mm"] = -12.5
    findings = validate_dataset(neg_df, generate_reports=False)
    assert findings["is_valid"] is False
    assert any("negative values" in err for err in findings["critical_errors"])


def test_validation_detects_monotonicity_violation(valid_synthetic_df):
    non_monotonic = valid_synthetic_df.copy()
    non_monotonic.loc[1, "rainfall_1h_mm"] = 50.0
    non_monotonic.loc[1, "rainfall_3h_mm"] = 10.0  # 1h > 3h
    findings = validate_dataset(non_monotonic, generate_reports=False)
    assert findings["is_valid"] is False
    assert findings["consistency"]["violations_1h_gt_3h"] > 0
    assert any("monotonicity violation" in err for err in findings["critical_errors"])


# 2. Training Pipeline Execution & Model Serialization
def test_training_pipeline_and_serialization():
    # Use workspace synthetic dataset
    csv_file = PROJECT_ROOT / "waterwatch_ai_nagpur_localities.csv"
    assert csv_file.exists(), f"Missing primary dataset: {csv_file}"

    out = train_and_evaluate(csv_path=str(csv_file))
    assert "best_model_name" in out
    assert "eval_results" in out
    assert "metadata" in out

    best_name = out["best_model_name"]
    metrics = out["eval_results"][best_name]

    # Verify metrics exist and within valid statistical bounds
    assert 0.0 <= metrics["accuracy"] <= 1.0
    assert 0.0 <= metrics["f1_score"] <= 1.0
    if metrics["roc_auc"] is not None:
        assert 0.0 <= metrics["roc_auc"] <= 1.0

    # Test model artifact reload
    model_path = PROJECT_ROOT / "ml" / "rainfall" / "rainfall_model.joblib"
    assert model_path.exists()
    loaded_pipe = joblib.load(model_path)
    assert hasattr(loaded_pipe, "predict")
    assert hasattr(loaded_pipe, "predict_proba")

    # Metadata check
    meta_path = PROJECT_ROOT / "ml" / "rainfall" / "model_metadata.json"
    assert meta_path.exists()
    with open(meta_path, "r", encoding="utf-8") as f:
        meta = json.load(f)
    assert meta["model_name"] == best_name
    assert meta["feature_schema"]["feature_order"] == FEATURE_COLUMNS


# 3. Prediction Input Validation & Output Schema
def test_prediction_input_validation_valid():
    valid_input = {
        "rainfall_1h_mm": 20.0,
        "rainfall_3h_mm": 35.0,
        "rainfall_6h_mm": 50.0,
        "rainfall_24h_mm": 80.0,
        "rainfall_prev_72h_mm": 110.0,
        "drainage_capacity_proxy": 0.45
    }
    cleaned, warnings = validate_input_features(valid_input)
    assert len(cleaned) == 6
    assert cleaned["rainfall_1h_mm"] == 20.0
    assert len(warnings) == 0


def test_prediction_input_missing_fields():
    incomplete_input = {
        "rainfall_1h_mm": 20.0,
        "rainfall_3h_mm": 35.0
        # Missing other 4 fields
    }
    with pytest.raises(FeatureValidationError) as exc_info:
        validate_input_features(incomplete_input)
    assert "Missing required rainfall features" in str(exc_info.value)


def test_prediction_input_negative_values():
    neg_input = {
        "rainfall_1h_mm": -5.0,
        "rainfall_3h_mm": 35.0,
        "rainfall_6h_mm": 50.0,
        "rainfall_24h_mm": 80.0,
        "rainfall_prev_72h_mm": 110.0,
        "drainage_capacity_proxy": 0.45
    }
    with pytest.raises(FeatureValidationError) as exc_info:
        validate_input_features(neg_input)
    assert "cannot be negative" in str(exc_info.value)


def test_prediction_strict_monotonic_check():
    non_mono = {
        "rainfall_1h_mm": 40.0,
        "rainfall_3h_mm": 20.0,  # 1h > 3h
        "rainfall_6h_mm": 50.0,
        "rainfall_24h_mm": 80.0,
        "rainfall_prev_72h_mm": 110.0,
        "drainage_capacity_proxy": 0.45
    }
    with pytest.raises(FeatureValidationError) as exc_info:
        validate_input_features(non_mono, strict_monotonic=True)
    assert "Inconsistent cumulative rainfall windows" in str(exc_info.value)


def test_prediction_output_schema():
    valid_input = {
        "rainfall_1h_mm": 30.0,
        "rainfall_3h_mm": 55.0,
        "rainfall_6h_mm": 75.0,
        "rainfall_24h_mm": 95.0,
        "rainfall_prev_72h_mm": 130.0,
        "drainage_capacity_proxy": 0.35
    }
    res = predict_waterlogging(valid_input)

    assert "predicted_class" in res and res["predicted_class"] in [0, 1]
    assert "waterlogging_predicted" in res and isinstance(res["waterlogging_predicted"], bool)
    assert "model_score" in res and 0.0 <= res["model_score"] <= 1.0
    assert "risk_category" in res and res["risk_category"] in ["LOW", "MODERATE", "HIGH"]
    assert "model_name" in res
    assert "model_version" in res
    assert res["training_data_status"] == "SYNTHETIC_EXPERIMENTAL"
    assert "scientific_disclaimer" in res


def test_missing_model_file_raises_error():
    """Verify that absent model path raises ModelLoadError rather than fabricating predictions."""
    fake_path = PROJECT_ROOT / "models" / "rainfall" / "non_existent_fake_model.joblib"
    with pytest.raises(ModelLoadError) as exc_info:
        load_model_and_metadata(fake_path)
    assert "Specified model path does not exist" in str(exc_info.value)


# 4. Image Inference Graceful Error Handling
def test_image_inference_missing_weights():
    """Verify image inference gracefully fails or raises when weights are invalid."""
    from scripts.predict_image import predict
    import numpy as np

    dummy_img = np.zeros((100, 100, 3), dtype=np.uint8)
    with tempfile.NamedTemporaryFile(suffix=".jpg", delete=False) as tmp:
        tmp_name = tmp.name

    try:
        from PIL import Image
        Image.fromarray(dummy_img).save(tmp_name)

        # Run with invalid weights path
        with pytest.raises(Exception):
            predict(source_path=tmp_name, weights_path="non_existent_weights_xyz123.pt")
    finally:
        if os.path.exists(tmp_name):
            os.remove(tmp_name)


# 5. Unblocked Training & Script Prediction Tests
def test_unblocked_scripts_train_rainfall_model():
    """Verify scripts/train_rainfall_model.py trains experimental model on sample CSV without error."""
    from scripts.train_rainfall_model import train_or_establish_baseline
    train_or_establish_baseline()

    model_path = PROJECT_ROOT / "models" / "rainfall" / "synthetic_rainfall_model.joblib"
    assert model_path.exists(), "synthetic_rainfall_model.joblib must be created"

    report_path = PROJECT_ROOT / "reports" / "rainfall_model_training_report.md"
    assert report_path.exists()
    content = report_path.read_text(encoding="utf-8")
    assert "SYNTHETIC_EXPERIMENTAL" in content
    assert "READY" in content


def test_scripts_predict_rainfall_experimental():
    """Verify predict_experimental_rainfall in scripts/predict_rainfall.py."""
    from scripts.predict_rainfall import predict_experimental_rainfall
    res = predict_experimental_rainfall(
        rainfall_1h_mm=25.0,
        rainfall_3h_mm=45.0,
        rainfall_6h_mm=65.0,
        rainfall_24h_mm=95.0,
        rainfall_prev_72h_mm=130.0,
        drainage_capacity_proxy=0.35,
        location="Manish Nagar"
    )
    assert res["predicted_class"] in [0, 1]
    assert 0.0 <= res["predicted_probability"] <= 1.0
    assert res["risk_category"] in ["LOW", "MODERATE", "HIGH"]
    assert res["training_data_status"] == "SYNTHETIC_EXPERIMENTAL"
    assert "EXPERIMENTAL MODEL WARNING" in res["warning"]


def test_scripts_generate_predictions_report():
    """Verify batch sample predictions generation."""
    from scripts.predict_rainfall import generate_predictions_report
    report = generate_predictions_report()
    assert len(report["sample_rows_predictions"]) >= 10
    assert len(report["locality_predictions"]) == 6
    assert len(report["scenario_predictions"]) >= 4

    md_file = PROJECT_ROOT / "reports" / "sample_predictions_report.md"
    json_file = PROJECT_ROOT / "reports" / "sample_predictions.json"
    assert md_file.exists()
    assert json_file.exists()


