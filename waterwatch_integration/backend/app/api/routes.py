"""
WaterWatch AI Integration - Intelligent Routing API Router
"""

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from waterwatch_integration.backend.app.database.connection import get_db
from waterwatch_integration.backend.app.database.models import Incident, RoadClosure, HistoricalHotspot, CitizenReport
from waterwatch_integration.backend.app.schemas.routing import RouteRecommendationRequest, RouteRecommendationResponse
from waterwatch_integration.backend.app.services.routing_service import routing_service

router = APIRouter(tags=["Intelligent Route Recommendations"])


@router.post("/routes/recommend", response_model=RouteRecommendationResponse)
def get_route_recommendations(payload: RouteRecommendationRequest, db: Session = Depends(get_db)):
    """
    Computes alternative candidate routes and scores waterlogging risk against active hazards.
    """
    active_incidents = db.query(Incident).filter(Incident.status == "Active").all()
    road_closures = db.query(RoadClosure).filter(RoadClosure.status == "Active").all()
    hotspots = db.query(HistoricalHotspot).all()
    citizen_reports = db.query(CitizenReport).all()

    try:
        evaluated_routes = routing_service.plan_routes(
            origin_lat=payload.origin.latitude,
            origin_lon=payload.origin.longitude,
            dest_lat=payload.destination.latitude,
            dest_lon=payload.destination.longitude,
            travel_mode=payload.travel_mode,
            preference=payload.preference,
            active_incidents=active_incidents,
            road_closures=road_closures,
            historical_hotspots=hotspots,
            citizen_reports=citizen_reports
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Routing recommendation error: {str(e)}")

    return {
        "origin": payload.origin,
        "destination": payload.destination,
        "requested_preference": payload.preference,
        "candidates_count": len(evaluated_routes),
        "routes": evaluated_routes
    }
