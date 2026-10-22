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


@router.get("/predictions/table")
def get_prediction_table(rain_multiplier: float = 1.0):
    """
    Computes strict ML predictions directly from models/rainfall/synthetic_rainfall_model.joblib
    for all monitored localities across Nagpur.
    """
    if not rainfall_adapter.is_available():
        raise HTTPException(
            status_code=503,
            detail="Experimental rainfall model artifact is currently unavailable at models/rainfall/synthetic_rainfall_model.joblib."
        )

    localities = [
        {"name": "Pardi Naka Underpass", "lat": 21.1442, "lng": 79.1415, "drainage": 0.22, "rain_1h": 28.5, "rain_3h": 36.2, "rain_6h": 45.0, "rain_24h": 68.0, "rain_prev_72h": 92.0},
        {"name": "Ambazari Lake Road", "lat": 21.1278, "lng": 79.0494, "drainage": 0.38, "rain_1h": 22.0, "rain_3h": 31.0, "rain_6h": 41.5, "rain_24h": 58.0, "rain_prev_72h": 81.0},
        {"name": "Pratap Nagar Square", "lat": 21.1189, "lng": 79.0628, "drainage": 0.42, "rain_1h": 18.0, "rain_3h": 26.5, "rain_6h": 38.0, "rain_24h": 52.0, "rain_prev_72h": 74.0},
        {"name": "Manewada Road Bridge", "lat": 21.1075, "lng": 79.0963, "drainage": 0.45, "rain_1h": 16.5, "rain_3h": 24.0, "rain_6h": 35.0, "rain_24h": 49.0, "rain_prev_72h": 70.0},
        {"name": "Manish Nagar Crossing", "lat": 21.0920, "lng": 79.0780, "drainage": 0.35, "rain_1h": 21.0, "rain_3h": 29.0, "rain_6h": 39.0, "rain_24h": 54.0, "rain_prev_72h": 76.0},
        {"name": "Dharampeth Main Road", "lat": 21.1458, "lng": 79.0664, "drainage": 0.68, "rain_1h": 8.0, "rain_3h": 14.5, "rain_6h": 22.0, "rain_24h": 38.0, "rain_prev_72h": 55.0},
        {"name": "Sitabuldi Interchange", "lat": 21.1466, "lng": 79.0882, "drainage": 0.65, "rain_1h": 7.5, "rain_3h": 13.0, "rain_6h": 20.5, "rain_24h": 35.0, "rain_prev_72h": 52.0},
        {"name": "Narendra Nagar Flyover", "lat": 21.1092, "lng": 79.0815, "drainage": 0.70, "rain_1h": 6.0, "rain_3h": 11.0, "rain_6h": 18.0, "rain_24h": 32.0, "rain_prev_72h": 48.0},
        {"name": "Civil Lines VIP Road", "lat": 21.1595, "lng": 79.0768, "drainage": 0.88, "rain_1h": 2.0, "rain_3h": 4.5, "rain_6h": 8.0, "rain_24h": 15.0, "rain_prev_72h": 25.0},
        {"name": "Sadar Residency Road", "lat": 21.1610, "lng": 79.0820, "drainage": 0.75, "rain_1h": 4.0, "rain_3h": 7.0, "rain_6h": 12.0, "rain_24h": 22.0, "rain_prev_72h": 35.0},
    ]

    mult = max(0.1, min(5.0, rain_multiplier))
    table_rows = []

    for loc in localities:
        features = {
            "rainfall_1h_mm": round(loc["rain_1h"] * mult, 2),
            "rainfall_3h_mm": round(loc["rain_3h"] * mult, 2),
            "rainfall_6h_mm": round(loc["rain_6h"] * mult, 2),
            "rainfall_24h_mm": round(loc["rain_24h"] * mult, 2),
            "rainfall_prev_72h_mm": round(loc["rain_prev_72h"] * mult, 2),
            "drainage_capacity_proxy": loc["drainage"]
        }
        res = rainfall_adapter.predict(features, locality=loc["name"])
        table_rows.append({
            "locality": loc["name"],
            "latitude": loc["lat"],
            "longitude": loc["lng"],
            "rainfall_1h_mm": features["rainfall_1h_mm"],
            "rainfall_3h_mm": features["rainfall_3h_mm"],
            "rainfall_6h_mm": features["rainfall_6h_mm"],
            "rainfall_24h_mm": features["rainfall_24h_mm"],
            "rainfall_prev_72h_mm": features["rainfall_prev_72h_mm"],
            "drainage_capacity_proxy": loc["drainage"],
            "predicted_class": res["predicted_class"],
            "waterlogging_predicted": res["waterlogging_predicted"],
            "predicted_probability": res["predicted_probability"],
            "predicted_probability_pct": round(res["predicted_probability"] * 100, 1),
            "risk_category": res["risk_category"],
            "model_status": res["training_data_status"]
        })

    return {
        "model_name": "LogisticRegression (StandardScaler pipeline)",
        "model_artifact": "models/rainfall/synthetic_rainfall_model.joblib",
        "training_data_status": "SYNTHETIC_EXPERIMENTAL (Strict ML)",
        "total_localities": len(table_rows),
        "rain_multiplier_applied": mult,
        "predictions": table_rows
    }

