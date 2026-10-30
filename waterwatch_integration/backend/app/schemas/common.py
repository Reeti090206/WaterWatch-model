"""
WaterWatch AI Integration - Common Pydantic Schemas
"""

from typing import Optional, List, Dict, Any
from pydantic import BaseModel, Field


class HealthResponse(BaseModel):
    status: str = "healthy"
    version: str = "1.0.0"
    app_name: str
    database_connected: bool
    models_available: Dict[str, bool]


class Coordinates(BaseModel):
    latitude: float = Field(..., ge=-90.0, le=90.0)
    longitude: float = Field(..., ge=-180.0, le=180.0)


class IncidentResponse(BaseModel):
    id: int
    incident_code: str
    title: str
    location_name: str
    latitude: float
    longitude: float
    severity: str
    water_depth_cm: Optional[float] = None
    is_verified: bool
    source: str
    status: str
    created_at: str

    class Config:
        from_attributes = True


class HistoricalHotspotResponse(BaseModel):
    id: int
    hotspot_code: str
    name: str
    locality: str
    latitude: float
    longitude: float
    incident_count_last_5yr: int
    chronic_cause: str
    average_depth_cm: float
    drainage_capacity_proxy: float
    typical_critical_threshold_mm: float

    class Config:
        from_attributes = True


class RoadClosureResponse(BaseModel):
    id: int
    closure_code: str
    road_name: str
    locality: str
    latitude: float
    longitude: float
    reason: str
    status: str
    reported_at: str

    class Config:
        from_attributes = True
