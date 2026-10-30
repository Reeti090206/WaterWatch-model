"""
WaterWatch AI - Comprehensive Integration Tests
Validates all backend APIs, ML model adapters, database operations,
routing service, citizen reporting, and strict preservation of root workspace.
"""

import sys
import io
import subprocess
from pathlib import Path
import pytest
from fastapi.testclient import TestClient
from PIL import Image

# Ensure root is in path
ROOT_DIR = Path(__file__).resolve().parent.parent.parent.parent
if str(ROOT_DIR) not in sys.path:
    sys.path.insert(0, str(ROOT_DIR))

from waterwatch_integration.backend.app.main import app
from waterwatch_integration.backend.app.config import settings
from waterwatch_integration.backend.app.database.models import init_db

init_db()
client = TestClient(app)



def test_root_files_untouched():
    """Verify that git tracks zero unexpected deleted files outside allowed pipeline directories."""
    result = subprocess.run(
        ["git", "status", "--porcelain"],
        cwd=str(ROOT_DIR),
        capture_output=True,
        text=True,
    )
    assert result.returncode == 0
    for line in result.stdout.splitlines():
        if not line.strip():
            continue
        status = line[:2]
        filepath = line[3:].strip()
        # Ensure no core repository documentation or config files are accidentally deleted
        if not filepath.startswith("waterwatch_integration") and not filepath.startswith("data/"):
            assert "D" not in status, f"Root workspace file deleted: {filepath}"


def test_health_endpoint():
    response = client.get("/api/v1/health")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "healthy"
    assert data["database_connected"] is True
    assert "models_available" in data


def test_models_status_provenance():
    """Verify model status and transparent synthetic experimental tagging."""
    response = client.get("/api/v1/models/status")
    assert response.status_code == 200
    data = response.json()
    assert "rainfall_model" in data
    assert "image_model" in data
    assert "READY" in data["rainfall_model"]["readiness"]
    assert data["rainfall_model"]["training_data_status"] == "SYNTHETIC_EXPERIMENTAL"
    assert data["production_model"]["status"] == "BLOCKED ON DATA"


def test_maps_config_endpoint():
    """Verify Google Maps configuration endpoint."""
    response = client.get("/api/v1/config/maps")
    assert response.status_code == 200
    data = response.json()
    assert data["google_maps_api_key"] == settings.google_maps_api_key
    assert data["provider"] == "google_maps"


def test_dashboard_summary():
    response = client.get("/api/v1/dashboard/summary")
    assert response.status_code == 200
    data = response.json()
    assert "metrics" in data
    assert "total_incidents" in data["metrics"]
    assert "chronic_hotspots" in data["metrics"]
    assert "live_weather" in data
    assert "system_status" in data


def test_hotspots_list():
    response = client.get("/api/v1/hotspots")
    assert response.status_code == 200
    hotspots = response.json()
    assert isinstance(hotspots, list)
    assert len(hotspots) >= 4  # Seeded with Nagpur hotspots
    names = [h["name"] for h in hotspots]
    assert any("Mor Bhavan" in n or "Sitabuldi" in n or "Underpass" in n for n in names)


def test_road_closures_list():
    response = client.get("/api/v1/road-closures")
    assert response.status_code == 200
    closures = response.json()
    assert isinstance(closures, list)


def test_rainfall_prediction_flow():
    """Test rainfall ML prediction endpoint using synthetic rainfall model."""
    payload = {
        "locality_name": "Sitabuldi Square",
        "rainfall_1h_mm": 45.0,
        "rainfall_3h_mm": 80.0,
        "rainfall_6h_mm": 110.0,
        "rainfall_24h_mm": 130.0,
        "rainfall_prev_72h_mm": 150.0,
        "drainage_capacity_proxy": 0.40
    }
    response = client.post("/api/v1/predictions/rainfall", json=payload)
    assert response.status_code == 200
    res = response.json()
    assert "predicted_probability" in res
    assert "risk_category" in res
    assert res["training_data_status"] == "SYNTHETIC_EXPERIMENTAL"
    assert "EXPERIMENTAL MODEL INFERENCE" in res["scientific_disclaimer"]


def test_citizen_report_submission_and_review():
    """Test report creation and authority moderation flow."""
    form_data = {
        "location_name": "Dharampeth Test Alert",
        "latitude": "21.1415",
        "longitude": "79.0620",
        "water_depth_cm": "30.0",
        "reporter_name": "Test Citizen",
        "reporter_contact": "9876543210",
        "description": "Road waterlogging near traffic signal",
        "estimated_severity": "Moderate"
    }
    res_post = client.post("/api/v1/reports", data=form_data)
    assert res_post.status_code == 200
    created = res_post.json()
    assert created["location_name"] == "Dharampeth Test Alert"
    assert created["verification_status"] == "UNVERIFIED"
    report_id = created["report_id"]


    # Review as authority: verify report
    review_data = {
        "action": "VERIFY",
        "reviewer_notes": "Verified by field warden",
        "admin_token": settings.admin_token
    }
    res_review = client.patch(f"/api/v1/reports/{report_id}/review", json=review_data)
    assert res_review.status_code == 200
    reviewed = res_review.json()
    assert reviewed["verification_status"] == "VERIFIED"

    # Verify incident was created
    res_incidents = client.get("/api/v1/incidents")
    assert res_incidents.status_code == 200
    incidents = res_incidents.json()
    assert any("Dharampeth Test Alert" in inc["location_name"] for inc in incidents)


def test_route_recommendation():
    """Test multi-criterion intelligent route recommendation for Nagpur."""
    payload = {
        "origin": {
            "name": "Chhatrapati Square",
            "latitude": 21.1070,
            "longitude": 79.0610
        },
        "destination": {
            "name": "Nagpur Railway Station",
            "latitude": 21.1524,
            "longitude": 79.0888
        },
        "travel_mode": "driving",
        "preference": "balanced"
    }
    response = client.post("/api/v1/routes/recommend", json=payload)
    assert response.status_code == 200
    data = response.json()
    assert "routes" in data
    assert len(data["routes"]) > 0
    route = data["routes"][0]
    assert "risk_score" in route
    assert "estimated_risk_level" in route
    assert "coordinates" in route
    assert len(route["coordinates"]) > 0


def test_image_detection_endpoint():
    """Test image detection endpoint with synthetic test image."""
    # Generate a small 100x100 RGB image in memory
    img = Image.new("RGB", (100, 100), color=(73, 109, 137))
    buf = io.BytesIO()
    img.save(buf, format="JPEG")
    buf.seek(0)

    response = client.post(
        "/api/v1/detection/image",
        files={"image": ("test_puddle.jpg", buf, "image/jpeg")},
        data={"conf_threshold": "0.25"}
    )
    assert response.status_code == 200
    result = response.json()
    assert "waterlogging_detected" in result
    assert "disclaimer" in result
