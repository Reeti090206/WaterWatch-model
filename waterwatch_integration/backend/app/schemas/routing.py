"""
WaterWatch AI Integration - Intelligent Routing Schemas
"""

from typing import Optional, List, Dict, Any
from pydantic import BaseModel, Field


class RoutePoint(BaseModel):
    name: Optional[str] = "Point"
    latitude: float = Field(..., ge=-90.0, le=90.0)
    longitude: float = Field(..., ge=-180.0, le=180.0)


class RouteRecommendationRequest(BaseModel):
    origin: RoutePoint
    destination: RoutePoint
    travel_mode: str = Field("driving", pattern="^(driving|walking|cycling)$")
    preference: str = Field("balanced", pattern="^(fastest|lowest_risk|balanced)$")


class RouteSegment(BaseModel):
    preference_type: str  # fastest, lowest_risk, balanced
    distance_km: float
    duration_minutes: float
    estimated_risk_level: str  # LOW_ESTIMATED_RISK, MODERATE_ESTIMATED_RISK, HIGH_ESTIMATED_RISK, UNKNOWN
    risk_score: float  # [0.0, 1.0]
    hazard_factors: List[str] = []
    coordinates: List[List[float]]  # [[lat, lon], ...]
    is_recommended: bool = False
    recommendation_rationale: str
    data_freshness_warning: Optional[str] = None


class RouteRecommendationResponse(BaseModel):
    origin: RoutePoint
    destination: RoutePoint
    requested_preference: str
    candidates_count: int
    routes: List[RouteSegment]
    disclaimer: str = (
        "Route recommendations evaluate proximity to active incidents, road closures, chronic hotspots, "
        "and experimental predictions. Never attempt to drive through flooded underpasses or high-water roads."
    )
