"""
WaterWatch AI Integration - Citizen Report Schemas
"""

from typing import Optional
from datetime import datetime
from pydantic import BaseModel, Field, ConfigDict


class CitizenReportCreate(BaseModel):
    location_name: str = Field(..., min_length=2, max_length=200)
    latitude: float = Field(..., ge=15.0, le=25.0)
    longitude: float = Field(..., ge=70.0, le=85.0)
    description: str = Field(..., min_length=5, max_length=1000)
    estimated_severity: str = Field("Moderate", pattern="^(Low|Moderate|High|Critical)$")
    water_depth_cm: Optional[float] = Field(None, ge=0.0, le=300.0)
    reporter_name: Optional[str] = "Anonymous Citizen"
    reporter_contact: Optional[str] = None


class CitizenReportReview(BaseModel):
    action: str = Field(..., pattern="^(VERIFY|REJECT|REQUEST_INFO)$")
    reviewer_notes: Optional[str] = None
    admin_token: str


class CitizenReportResponse(BaseModel):
    id: int
    report_code: str
    location_name: str
    latitude: float
    longitude: float
    description: str
    estimated_severity: str
    water_depth_cm: Optional[float] = None
    image_filename: Optional[str] = None
    verification_status: str
    reviewer_notes: Optional[str] = None
    reviewed_by: Optional[str] = None
    reviewed_at: Optional[str] = None
    created_at: str

    model_config = ConfigDict(from_attributes=True)
