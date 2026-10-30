"""
WaterWatch AI Integration - Incidents & Road Closures API Router
"""

from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from waterwatch_integration.backend.app.database.connection import get_db
from waterwatch_integration.backend.app.database.models import Incident, RoadClosure
from waterwatch_integration.backend.app.schemas.common import IncidentResponse, RoadClosureResponse

router = APIRouter(tags=["Incidents & Road Closures"])


@router.get("/incidents")
def list_incidents(
    status: Optional[str] = Query(None, description="Filter by status (Active, Resolved)"),
    severity: Optional[str] = Query(None, description="Filter by severity (Low, Moderate, High, Critical)"),
    db: Session = Depends(get_db)
):
    """Retrieves all waterlogging incidents for map display and list view."""
    query = db.query(Incident)
    if status:
        query = query.filter(Incident.status.ilike(status))
    if severity:
        query = query.filter(Incident.severity.ilike(severity))

    incidents = query.order_by(Incident.created_at.desc()).all()
    return [
        {
            "id": inc.id,
            "incident_code": inc.incident_code,
            "title": inc.title,
            "location_name": inc.location_name,
            "latitude": inc.latitude,
            "longitude": inc.longitude,
            "severity": inc.severity,
            "water_depth_cm": inc.water_depth_cm,
            "is_verified": inc.is_verified,
            "source": inc.source,
            "status": inc.status,
            "created_at": inc.created_at.isoformat()
        }
        for inc in incidents
    ]


@router.get("/incidents/{incident_id}")
def get_incident(incident_id: int, db: Session = Depends(get_db)):
    """Fetches details for a specific incident."""
    inc = db.query(Incident).filter(Incident.id == incident_id).first()
    if not inc:
        raise HTTPException(status_code=404, detail="Incident not found")
    return {
        "id": inc.id,
        "incident_code": inc.incident_code,
        "title": inc.title,
        "location_name": inc.location_name,
        "latitude": inc.latitude,
        "longitude": inc.longitude,
        "severity": inc.severity,
        "water_depth_cm": inc.water_depth_cm,
        "is_verified": inc.is_verified,
        "source": inc.source,
        "status": inc.status,
        "created_at": inc.created_at.isoformat()
    }


@router.get("/road-closures")
def list_road_closures(db: Session = Depends(get_db)):
    """Retrieves active road closures across Nagpur."""
    closures = db.query(RoadClosure).filter(RoadClosure.status == "Active").all()
    return [
        {
            "id": c.id,
            "closure_code": c.closure_code,
            "road_name": c.road_name,
            "locality": c.locality,
            "latitude": c.latitude,
            "longitude": c.longitude,
            "reason": c.reason,
            "status": c.status,
            "reported_at": c.reported_at.isoformat()
        }
        for c in closures
    ]
