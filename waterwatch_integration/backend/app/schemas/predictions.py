"""
WaterWatch AI Integration - Rainfall Prediction Schemas
"""

from typing import Optional, Dict, Any, List
from pydantic import BaseModel, Field


class RainfallPredictionRequest(BaseModel):
    rainfall_1h_mm: float = Field(..., ge=0.0, le=300.0, description="1-hour rainfall accumulation in mm")
    rainfall_3h_mm: float = Field(..., ge=0.0, le=500.0, description="3-hour rainfall accumulation in mm")
    rainfall_6h_mm: float = Field(..., ge=0.0, le=800.0, description="6-hour rainfall accumulation in mm")
    rainfall_24h_mm: float = Field(..., ge=0.0, le=1200.0, description="24-hour rainfall accumulation in mm")
    rainfall_prev_72h_mm: float = Field(..., ge=0.0, le=2000.0, description="Previous 72-hour antecedent rainfall in mm")
    drainage_capacity_proxy: float = Field(0.50, ge=0.0, le=1.0, description="Estimated drainage clearance rate [0.0, 1.0]")
    locality_name: Optional[str] = "Nagpur Central"


class RainfallPredictionResponse(BaseModel):
    location: str
    predicted_class: int
    waterlogging_predicted: bool
    predicted_probability: float
    risk_category: str
    model_name: str
    model_version: str
    training_data_status: str = "SYNTHETIC_EXPERIMENTAL"
    validation_warnings: List[str] = []
    input_features: Dict[str, float]
    scientific_disclaimer: str
