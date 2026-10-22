"""
WaterWatch AI Integration - Dashboard & System Status Endpoints
"""

from datetime import datetime
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from waterwatch_integration.backend.app.config import settings, RAINFALL_MODEL_PATH, METEOROLOGICAL_BASELINE_PATH, IMAGE_MODEL_PATH
from waterwatch_integration.backend.app.database.connection import get_db
from waterwatch_integration.backend.app.database.models import Incident, CitizenReport, HistoricalHotspot, RoadClosure, PredictionAudit
from waterwatch_integration.backend.app.adapters.rainfall_adapter import rainfall_adapter
from waterwatch_integration.backend.app.adapters.image_adapter import image_adapter
from waterwatch_integration.backend.app.adapters.weather_adapter import weather_adapter

router = APIRouter(tags=["Dashboard & Health"])


@router.get("/health")
def get_health(db: Session = Depends(get_db)):
    """Healthcheck endpoint verifying DB and model availability."""
    db_ok = True
    try:
        db.query(Incident).count()
    except Exception:
        db_ok = False

    return {
        "status": "healthy",
        "app_name": settings.app_name,
        "version": settings.version,
        "timestamp": datetime.utcnow().isoformat(),
        "database_connected": db_ok,
        "models_available": {
            "synthetic_rainfall_model": rainfall_adapter.is_available(),
            "meteorological_baseline": METEOROLOGICAL_BASELINE_PATH.exists(),
            "image_yolo_model": image_adapter.is_available()
        }
    }


@router.get("/dashboard/summary")
def get_dashboard_summary(db: Session = Depends(get_db)):
    """Provides key operational metrics for the frontend main dashboard."""
    total_incidents = db.query(Incident).count()
    verified_incidents = db.query(Incident).filter(Incident.is_verified == True).count()
    unverified_reports = db.query(CitizenReport).filter(CitizenReport.verification_status == "UNVERIFIED").count()
    active_closures = db.query(RoadClosure).filter(RoadClosure.status == "Active").count()
    total_hotspots = db.query(HistoricalHotspot).count()
    predictions_count = db.query(PredictionAudit).count()

    # Active risk levels
    high_risk_locs = db.query(Incident).filter(Incident.severity.in_(["High", "Critical"])).count()
    med_risk_locs = db.query(Incident).filter(Incident.severity == "Moderate").count()

    live_weather = weather_adapter.get_live_weather()

    return {
        "metrics": {
            "total_incidents": total_incidents,
            "verified_waterlogging_incidents": verified_incidents,
            "unverified_citizen_reports": unverified_reports,
            "active_road_closures": active_closures,
            "chronic_hotspots": total_hotspots,
            "high_risk_locations": high_risk_locs,
            "medium_risk_locations": med_risk_locs,
            "total_predictions_served": predictions_count
        },
        "live_weather": live_weather,
        "system_status": {
            "experimental_rainfall_model": "READY (SYNTHETIC_EXPERIMENTAL)",
            "verified_production_model": "BLOCKED ON DATA (Awaiting NMC Incident Logs)",
            "image_detection_model": "READY (Optical Surface Detection)",
            "routing_engine": "ACTIVE (OSRM Road Network + Flood Hazard Scoring)"
        },
        "last_updated": datetime.utcnow().isoformat()
    }


@router.get("/status")
def get_system_status():
    """System status and provenance statement."""
    return {
        "project": "WaterWatch AI — Nagpur Full-Stack Integration",
        "city": "Nagpur, Maharashtra, India",
        "timestamp": datetime.utcnow().isoformat(),
        "readiness_matrix": {
            "experimental_synthetic_model": {
                "status": "READY",
                "scope": "Experimental pipeline, API contract verification, and routing tests.",
                "provenance": "SYNTHETIC_EXPERIMENTAL"
            },
            "verified_nagpur_production_model": {
                "status": "BLOCKED ON DATA",
                "scope": "Requires ground-truth municipal incident logs from NMC or traffic police.",
                "provenance": "OFFICIAL_MUNICIPAL"
            },
            "image_detection_yolov11": {
                "status": "EXPERIMENTAL_READY",
                "scope": "Surface water visual detection. Does not measure flood depth in cm."
            }
        }
    }


@router.get("/models/status")
def get_models_status():
    """Detailed model status cards."""
    return {
        "rainfall_model": rainfall_adapter.get_status(),
        "image_model": image_adapter.get_status(),
        "weather_service": weather_adapter.get_live_weather(),
        "production_model": {
            "status": "BLOCKED ON DATA",
            "message": "Preserved for genuine municipal ground truth. Awaiting NMC incident records."
        }
    }


@router.get("/config/maps")
def get_maps_config():
    """Returns Google Maps configuration and credentials."""
    return {
        "google_maps_api_key": settings.google_maps_api_key,
        "default_center": {"lat": 21.1458, "lng": 79.0882},
        "default_zoom": 13,
        "provider": "google_maps"
    }


