"""
WaterWatch AI Integration - Rainfall Observations & Prediction API Router
"""

import json
from datetime import datetime
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from waterwatch_integration.backend.app.database.connection import get_db
from waterwatch_integration.backend.app.database.models import PredictionAudit
from waterwatch_integration.backend.app.schemas.predictions import RainfallPredictionRequest, RainfallPredictionResponse
from waterwatch_integration.backend.app.adapters.rainfall_adapter import rainfall_adapter
from waterwatch_integration.backend.app.adapters.weather_adapter import weather_adapter

router = APIRouter(tags=["Rainfall & ML Predictions"])


@router.get("/rainfall/observations")
def get_rainfall_observations():
    """Returns current rainfall and meteorological observations for Nagpur."""
    weather = weather_adapter.get_live_weather()
    return {
        "status": weather.get("status"),
        "city": "Nagpur, Maharashtra",
        "current_precipitation_mm": weather.get("current_precipitation_mm"),
        "current_rain_mm": weather.get("current_rain_mm"),
        "temperature_celsius": weather.get("temperature_celsius"),
        "humidity_percent": weather.get("humidity_percent"),
        "observation_time": weather.get("observation_time"),
        "source": weather.get("source"),
        "message": weather.get("message")
    }


@router.post("/predictions/rainfall", response_model=RainfallPredictionResponse)
def predict_waterlogging_risk(payload: RainfallPredictionRequest, db: Session = Depends(get_db)):
    """
    Infers waterlogging risk using the trained experimental synthetic model.
    """
    if not rainfall_adapter.is_available():
        raise HTTPException(
            status_code=503,
            detail="Experimental rainfall model artifact is currently unavailable. Ensure models/rainfall/synthetic_rainfall_model.joblib exists."
        )

    features = {
        "rainfall_1h_mm": payload.rainfall_1h_mm,
        "rainfall_3h_mm": payload.rainfall_3h_mm,
        "rainfall_6h_mm": payload.rainfall_6h_mm,
        "rainfall_24h_mm": payload.rainfall_24h_mm,
        "rainfall_prev_72h_mm": payload.rainfall_prev_72h_mm,
        "drainage_capacity_proxy": payload.drainage_capacity_proxy
    }

    try:
        result = rainfall_adapter.predict(features, locality=payload.locality_name or "Nagpur")
    except ValueError as ve:
        raise HTTPException(status_code=400, detail=str(ve))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Prediction inference failed: {str(e)}")

    # Audit log to DB
    try:
        audit = PredictionAudit(
            location=payload.locality_name or "Nagpur",
            rainfall_1h_mm=payload.rainfall_1h_mm,
            rainfall_24h_mm=payload.rainfall_24h_mm,
            predicted_class=result["predicted_class"],
            predicted_probability=result["predicted_probability"],
            risk_category=result["risk_category"],
            model_name=result["model_name"],
            training_data_status=result["training_data_status"],
            created_at=datetime.utcnow()
        )
        db.add(audit)
        db.commit()
    except Exception:
        db.rollback()

    return result


@router.get("/predictions/history")
def get_prediction_history(db: Session = Depends(get_db)):
    """Retrieves recent prediction audit logs."""
    logs = db.query(PredictionAudit).order_by(PredictionAudit.created_at.desc()).limit(20).all()
    return [
        {
            "id": l.id,
            "location": l.location,
            "rainfall_1h_mm": l.rainfall_1h_mm,
            "rainfall_24h_mm": l.rainfall_24h_mm,
            "predicted_class": l.predicted_class,
            "predicted_probability": l.predicted_probability,
            "risk_category": l.risk_category,
            "training_data_status": l.training_data_status,
            "created_at": l.created_at.isoformat()
        }
        for l in logs
    ]
