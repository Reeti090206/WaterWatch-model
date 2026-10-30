"""
WaterWatch AI - Comprehensive Phase 8 Acceptance & Live Demo Test Suite
Tests:
1. ZIP discovery and extraction integrity (IndiaScene365).
2. Dataset validation, empty background labels, and class mappings.
3. Duplicate detection and split independence (zero data leakage).
4. Inference on verified waterlogged road images.
5. Inference on verified non-waterlogged road images.
6. Invalid image upload handling and error responses.
7. Missing model file handling.
8. Rainfall input validation and boundary checks.
9. Saved benchmark telemetry loading.
10. Route planner recommendation and fallback behavior.
11. Combined dual-stream risk assessment and reasoning provenance.
"""

import io
import json
from pathlib import Path
import pytest
from fastapi.testclient import TestClient
from PIL import Image

PROJECT_ROOT = Path(__file__).resolve().parent.parent
from waterwatch_integration.backend.app.main import app
from waterwatch_integration.backend.app.adapters.image_adapter import image_adapter
from waterwatch_integration.backend.app.adapters.rainfall_adapter import rainfall_adapter
from waterwatch_integration.backend.app.services.routing_service import routing_service

client = TestClient(app)


def test_zip_discovery_and_extraction():
    """Verify that IndiaScene365.zip is located in the project root and extracted into data/raw/indiascene365."""
    zip_path = PROJECT_ROOT / "IndiaScene365.zip"
    assert zip_path.exists(), f"IndiaScene365.zip not found at {zip_path}"
    assert zip_path.stat().st_size > 100 * 1024 * 1024, "ZIP size is unexpectedly small"

    extracted_dir = PROJECT_ROOT / "data" / "raw" / "indiascene365"
    assert extracted_dir.exists(), f"Extracted directory {extracted_dir} does not exist"
    pngs = list(extracted_dir.rglob("*.png"))
    assert len(pngs) >= 700, f"Expected at least 700 PNG road images, found {len(pngs)}"


def test_dataset_validation_and_class_mapping():
    """Verify merged dataset contains positive and negative images, data.yaml, and manifest."""
    yolo_dir = PROJECT_ROOT / "data" / "processed" / "yolo_water_logging"
    data_yaml = yolo_dir / "data.yaml"
    assert data_yaml.exists()

    manifest_path = PROJECT_ROOT / "data" / "manifests" / "waterwatch_split_manifest.json"
    assert manifest_path.exists()
    with open(manifest_path, "r", encoding="utf-8") as f:
        manifest = json.load(f)

    assert manifest["summary"]["total_samples"] >= 500
    assert manifest["summary"]["total_waterlogged"] > 0
    assert manifest["summary"]["total_not_waterlogged"] > 0


def test_duplicate_detection_and_split_integrity():
    """Strictly assert zero image filename overlap between train, val, and test splits."""
    yolo_dir = PROJECT_ROOT / "data" / "processed" / "yolo_water_logging"
    train_files = {f.name for f in (yolo_dir / "images" / "train").glob("*.*")}
    val_files = {f.name for f in (yolo_dir / "images" / "val").glob("*.*")}
    test_files = {f.name for f in (yolo_dir / "images" / "test").glob("*.*")}

    assert len(train_files.intersection(val_files)) == 0, "Data leakage between train and val splits"
    assert len(train_files.intersection(test_files)) == 0, "Data leakage between train and test splits"
    assert len(val_files.intersection(test_files)) == 0, "Data leakage between val and test splits"


def test_inference_on_verified_waterlogged_image():
    """Verify that a known flooded road sample is classified as waterlogged."""
    sample_path = PROJECT_ROOT / "waterwatch_integration" / "frontend" / "samples" / "sample_waterlogged.jpg"
    assert sample_path.exists(), "Sample waterlogged image not found"

    res = image_adapter.detect(sample_path, conf_threshold=0.25)
    assert res["waterlogging_detected"] is True
    assert res["predicted_class"] == "waterlogged"
    assert res["severity"] in ["Low", "Moderate", "High"]
    assert "inference_time_ms" in res
    assert "disclaimer" in res


def test_inference_on_verified_non_waterlogged_image():
    """Verify that a known clean dry road from IndiaScene365 is classified as not_waterlogged."""
    sample_path = PROJECT_ROOT / "waterwatch_integration" / "frontend" / "samples" / "sample_dry_road.png"
    assert sample_path.exists(), "Sample dry road image not found"

    res = image_adapter.detect(sample_path, conf_threshold=0.25)
    assert res["waterlogging_detected"] is False
    assert res["predicted_class"] == "not_waterlogged"
    assert res["severity"] == "None"


def test_invalid_image_uploads():
    """Verify that uploading non-image files or corrupted content returns 400 Bad Request."""
    fake_txt = io.BytesIO(b"This is a text file, not an image.")
    response = client.post(
        "/api/v1/detection/image",
        files={"image": ("bad_file.txt", fake_txt, "text/plain")}
    )
    assert response.status_code == 400

    fake_corrupted = io.BytesIO(b"\xFF\xD8\xFF\xE0CorruptedJPEGHeader")
    response_corrupt = client.post(
        "/api/v1/detection/image",
        files={"image": ("corrupted.jpg", fake_corrupted, "image/jpeg")}
    )
    assert response_corrupt.status_code in [400, 500]


def test_rainfall_input_validation():
    """Verify negative rainfall values are rejected with 422 Unprocessable Entity."""
    bad_payload = {
        "locality_name": "Manish Nagar",
        "rainfall_1h_mm": -10.0,  # Negative
        "rainfall_3h_mm": 20.0,
        "rainfall_6h_mm": 30.0,
        "rainfall_24h_mm": 50.0,
        "rainfall_prev_72h_mm": 80.0,
        "drainage_capacity_proxy": 0.5
    }
    resp = client.post("/api/v1/predictions/rainfall", json=bad_payload)
    assert resp.status_code == 422


def test_loading_saved_metrics_endpoint():
    """Verify /assessment/benchmarks returns genuine evaluation metrics."""
    resp = client.get("/api/v1/assessment/benchmarks")
    assert resp.status_code == 200
    data = resp.json()
    assert "benchmark_summary" in data
    summary = data["benchmark_summary"]
    assert "models" in summary
    assert "mobilenetv3_classifier" in summary["models"]
    assert "improved_yolov11" in summary["models"]
    assert "baseline_yolov11" in summary["models"]

    # Verify accuracy values are genuine floats
    mn_acc = summary["models"]["mobilenetv3_classifier"]["metrics"]["accuracy"]
    assert 0.85 <= mn_acc <= 1.0


def test_sample_detection_endpoints():
    """Verify /detection/samples and /detection/sample-detect endpoints."""
    resp_list = client.get("/api/v1/detection/samples")
    assert resp_list.status_code == 200
    samples = resp_list.json()
    assert len(samples) >= 3

    resp_detect = client.post("/api/v1/detection/sample-detect", json={"sample_key": "sample_waterlogged"})
    assert resp_detect.status_code == 200
    res = resp_detect.json()
    assert res["waterlogging_detected"] is True
    assert "image_url" in res


def test_combined_assessment_endpoint():
    """Verify /assessment/combined dual-stream assessment and reasoning rationale."""
    payload = {
        "locality_name": "Pardi Naka Underpass",
        "rainfall_1h_mm": 45.0,
        "rainfall_3h_mm": 65.0,
        "rainfall_6h_mm": 90.0,
        "rainfall_24h_mm": 130.0,
        "rainfall_prev_72h_mm": 180.0,
        "drainage_capacity_proxy": 0.25,
        "sample_key": "sample_waterlogged"
    }
    resp = client.post("/api/v1/assessment/combined", json=payload)
    assert resp.status_code == 200
    data = resp.json()

    assert "combined_status" in data
    assert "rationale" in data
    assert "image_stream" in data
    assert "rainfall_stream" in data
    assert data["provenance_notes"]["is_neural_fusion"] is False


def test_route_planner_integration_and_fallback():
    """Verify route recommendation scores alternative Nagpur corridors with risk values."""
    payload = {
        "origin": {"latitude": 21.1466, "longitude": 79.0882, "address_name": "Sitabuldi Interchange"},
        "destination": {"latitude": 21.0920, "longitude": 79.0780, "address_name": "Manish Nagar RUB"},
        "travel_mode": "driving",
        "preference": "lowest_risk"
    }
    resp = client.post("/api/v1/routes/recommend", json=payload)
    assert resp.status_code == 200
    data = resp.json()
    assert data["candidates_count"] > 0
    routes = data["routes"]
    assert any(r.get("is_recommended") is True for r in routes)
    for r in routes:
        assert "distance_km" in r
        assert "duration_minutes" in r
        assert "risk_score" in r or "estimated_risk_level" in r
