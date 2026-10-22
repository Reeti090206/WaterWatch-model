"""
WaterWatch AI Integration - Historical Hotspots & Analytics API Router
"""

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from waterwatch_integration.backend.app.database.connection import get_db
from waterwatch_integration.backend.app.database.models import HistoricalHotspot
from waterwatch_integration.backend.app.services.hotspot_service import hotspot_service

router = APIRouter(tags=["Hotspots & Analytics"])


@router.get("/hotspots")
def list_hotspots(db: Session = Depends(get_db)):
    """Lists chronic waterlogging hotspots in Nagpur."""
    hotspots = db.query(HistoricalHotspot).all()
    return [
        {
            "id": h.id,
            "hotspot_code": h.hotspot_code,
            "name": h.name,
            "locality": h.locality,
            "latitude": h.latitude,
            "longitude": h.longitude,
            "incident_count_last_5yr": h.incident_count_last_5yr,
            "chronic_cause": h.chronic_cause,
            "average_depth_cm": h.average_depth_cm,
            "drainage_capacity_proxy": h.drainage_capacity_proxy,
            "typical_critical_threshold_mm": h.typical_critical_threshold_mm
        }
        for h in hotspots
    ]


@router.get("/analytics/summary")
def get_analytics_summary(db: Session = Depends(get_db)):
    """Provides spatial cluster analytics across Nagpur localities."""
    return hotspot_service.get_hotspots_summary(db)
