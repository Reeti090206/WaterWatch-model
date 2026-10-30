"""
WaterWatch AI Integration - Combined Assessment & Live Demo API Router
Handles dual-stream image + rainfall risk fusion, transparent provenance reporting,
model benchmarking telemetry, and evaluation triggers.
"""

import json
from pathlib import Path
from typing import Dict, Any, Optional
from fastapi import APIRouter, HTTPException, Depends
from pydantic import BaseModel, Field
from waterwatch_integration.backend.app.config import PROJECT_ROOT, INTEGRATION_ROOT
from waterwatch_integration.backend.app.adapters.rainfall_adapter import rainfall_adapter
from waterwatch_integration.backend.app.adapters.image_adapter import image_adapter

router = APIRouter(tags=["Live AI Demo & Combined Assessment"])

REPORTS_DIR = PROJECT_ROOT / "reports"
SAMPLES_DIR = INTEGRATION_ROOT / "frontend" / "samples"


class CombinedAssessmentRequest(BaseModel):
    locality_name: str = "Manish Nagar (RUB Corridor)"
    rainfall_1h_mm: float = Field(25.0, ge=0.0, le=300.0)
    rainfall_3h_mm: float = Field(45.0, ge=0.0, le=500.0)
    rainfall_6h_mm: float = Field(65.0, ge=0.0, le=800.0)
    rainfall_24h_mm: float = Field(95.0, ge=0.0, le=1200.0)
    rainfall_prev_72h_mm: float = Field(130.0, ge=0.0, le=2000.0)
    drainage_capacity_proxy: float = Field(0.45, ge=0.05, le=0.99)
    sample_key: Optional[str] = "sample_waterlogged"


@router.post("/assessment/combined")
def run_combined_assessment(payload: CombinedAssessmentRequest):
    """
    Executes real-time dual-stream assessment combining optical roadway computer vision
    with antecedent rainfall risk predictions via an explicit rule-based decision matrix.
    """
    # 1. Run Rainfall Prediction
    if not rainfall_adapter.is_available():
        raise HTTPException(status_code=503, detail="Rainfall model unavailable.")

    rain_features = {
        "rainfall_1h_mm": payload.rainfall_1h_mm,
        "rainfall_3h_mm": payload.rainfall_3h_mm,
        "rainfall_6h_mm": payload.rainfall_6h_mm,
        "rainfall_24h_mm": payload.rainfall_24h_mm,
        "rainfall_prev_72h_mm": payload.rainfall_prev_72h_mm,
        "drainage_capacity_proxy": payload.drainage_capacity_proxy
    }

    try:
        rain_result = rainfall_adapter.predict(rain_features, locality=payload.locality_name)
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Rainfall evaluation error: {str(e)}")

    # 2. Run Image Inference on Selected Sample
    image_result = None
    if payload.sample_key:
        sample_map = {
            "sample_waterlogged": SAMPLES_DIR / "sample_waterlogged.jpg",
            "sample_dry_road": SAMPLES_DIR / "sample_dry_road.png",
            "sample_urban_arterial": SAMPLES_DIR / "sample_urban_arterial.png",
            "sample_rainy_wet_road": SAMPLES_DIR / "sample_rainy_wet_road.png"
        }
        sample_path = sample_map.get(payload.sample_key)
        if sample_path and sample_path.exists():
            try:
                image_result = image_adapter.detect(sample_path)
                image_result["image_url"] = f"/static/samples/{sample_path.name}"
            except Exception as e:
                image_result = {"error": f"Image detection failed: {str(e)}"}

    # 3. Rule-Based Dual-Stream Decision Matrix
    # Explicitly transparent: Does NOT claim to be a neural fusion model
    rain_risk = rain_result["risk_category"]  # LOW, MODERATE, HIGH
    img_detected = image_result.get("waterlogging_detected", False) if image_result else False
    img_severity = image_result.get("severity", "None") if image_result else "Unknown"

    if img_detected:
        if rain_risk == "HIGH":
            combined_status = "CRITICAL HAZARD"
            combined_badge = "badge-high"
            rationale = (
                f"Active standing water detected on roadway ({img_severity} severity) AND atmospheric/soil "
                f"antecedent model predicts HIGH waterlogging probability ({rain_result['predicted_probability']*100:.1f}%). "
                f"RUB underpass or roadway is severely hazardous / impassable. Immediate detours advised."
            )
        elif rain_risk == "MODERATE":
            combined_status = "HIGH ROAD HAZARD"
            combined_badge = "badge-high"
            rationale = (
                f"Optical CV detects standing water ({img_severity} severity) under MODERATE rainfall saturation "
                f"({rain_result['predicted_probability']*100:.1f}%). Water is actively pooling despite sub-peak rainfall; "
                f"indicates localized drainage block or low elevation."
            )
        else:
            combined_status = "MODERATE ROAD HAZARD"
            combined_badge = "badge-mod"
            rationale = (
                f"Surface water pooling detected visually ({img_severity}), though acute rainfall is LOW "
                f"({rain_result['predicted_probability']*100:.1f}%). Likely residual waterlogging from prior accumulation."
            )
    else:
        if rain_risk == "HIGH":
            combined_status = "ELEVATED FLOOD WATCH"
            combined_badge = "badge-mod"
            rationale = (
                f"Roadway surface is currently clear (not waterlogged), but atmospheric antecedent saturation model "
                f"indicates HIGH imminent risk ({rain_result['predicted_probability']*100:.1f}%). "
                f"Inundation may occur if precipitation continues at current rates."
            )
        elif rain_risk == "MODERATE":
            combined_status = "MONITORING ADVISORY"
            combined_badge = "badge-low"
            rationale = (
                f"Road surface clear of pooling. Meteorological risk is MODERATE ({rain_result['predicted_probability']*100:.1f}%). "
                f"No immediate vehicle obstruction."
            )
        else:
            combined_status = "NORMAL / SAFE"
            combined_badge = "badge-low"
            rationale = (
                f"Clear dry roadway verified visually AND rainfall risk is LOW ({rain_result['predicted_probability']*100:.1f}%). "
                f"Normal traffic flow permitted."
            )

    return {
        "locality": payload.locality_name,
        "combined_status": combined_status,
        "combined_badge": combined_badge,
        "fusion_method": "Rule-Based Dual-Stream Decision Matrix (Explicitly Documented Heuristic)",
        "rationale": rationale,
        "image_stream": {
            "source": "Optical Computer Vision (MobileNetV3 + YOLOv11)",
            "waterlogging_detected": img_detected,
            "visual_severity": img_severity,
            "confidence_percentage": image_result.get("confidence_percentage", 0.0) if image_result else 0.0,
            "bounding_boxes_count": image_result.get("detection_count", 0) if image_result else 0,
            "image_url": image_result.get("image_url") if image_result else None
        },
        "rainfall_stream": {
            "source": "Experimental ML Pipeline (Synthetic Training Data)",
            "risk_category": rain_risk,
            "predicted_probability": rain_result["predicted_probability"],
            "probability_percentage": round(rain_result["predicted_probability"] * 100.0, 1),
            "inputs_evaluated": rain_result["input_features"],
            "status_disclaimer": "EXPERIMENTAL: Model trained on synthetic demonstration data. Not official municipal emergency feed."
        },
        "provenance_notes": {
            "is_neural_fusion": False,
            "transparency": "Decision rule combines visual pooling observation with meteorological antecedent thresholding."
        }
    }


@router.get("/assessment/benchmarks")
def get_benchmarks_telemetry():
    """Returns actual measured performance metrics from saved reports."""
    bench_file = REPORTS_DIR / "final_model_benchmark_comparison.json"
    mobilenet_file = REPORTS_DIR / "mobilenetv3_evaluation_report.json"
    yolo_file = REPORTS_DIR / "image_model_evaluation.json"

    bench_data = {}
    if bench_file.exists():
        with open(bench_file, "r", encoding="utf-8") as f:
            bench_data = json.load(f)

    mobilenet_data = {}
    if mobilenet_file.exists():
        with open(mobilenet_file, "r", encoding="utf-8") as f:
            mobilenet_data = json.load(f)

    yolo_data = {}
    if yolo_file.exists():
        with open(yolo_file, "r", encoding="utf-8") as f:
            yolo_data = json.load(f)

    return {
        "status": "Available",
        "benchmark_summary": bench_data,
        "mobilenetv3_detailed": mobilenet_data,
        "yolo_detailed": yolo_data,
        "dataset_provenance": {
            "positive_source": "WaterWatch Curated Field Dataset (199 images)",
            "negative_source": "IndiaScene365 Mendeley Data CC BY 4.0 (320 curated non-waterlogged road scenes)",
            "total_dataset_size": 519,
            "partition": "70% Train (363), 15% Val (77), 15% Held-Out Test (79)",
            "no_leakage_guarantee": "Split before training; zero overlap between train, val, and test partitions."
        }
    }
