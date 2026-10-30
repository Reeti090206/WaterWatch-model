"""
WaterWatch AI Integration - Image Detection API Router
Provides live image inference, sample selection, and optical detection endpoints.
"""

import uuid
from pathlib import Path
from typing import List, Dict, Any
from fastapi import APIRouter, UploadFile, File, HTTPException, Form
from pydantic import BaseModel
from waterwatch_integration.backend.app.config import UPLOADS_DIR, INTEGRATION_ROOT
from waterwatch_integration.backend.app.adapters.image_adapter import image_adapter

router = APIRouter(tags=["Image Detection"])

SAMPLES_DIR = INTEGRATION_ROOT / "frontend" / "samples"


class SampleDetectionRequest(BaseModel):
    sample_key: str
    conf_threshold: float = 0.25


@router.get("/detection/samples")
def list_verified_samples():
    """Returns curated verified demo images representing positive, negative, and edge cases."""
    return [
        {
            "key": "sample_waterlogged",
            "name": "Verified Waterlogged Road (Nagpur Underpass Corridor)",
            "category": "waterlogged",
            "expected_label": "waterlogged",
            "description": "Severe standing water pooling across lanes under low clearance corridor.",
            "url": "/static/samples/sample_waterlogged.jpg",
            "provenance": "WaterWatch Curated Field Dataset"
        },
        {
            "key": "sample_dry_road",
            "name": "Verified Dry Road (IndiaScene365 Daytime)",
            "category": "not_waterlogged",
            "expected_label": "not_waterlogged",
            "description": "Clear daylight arterial road in India with dry asphalt and lane markers.",
            "url": "/static/samples/sample_dry_road.png",
            "provenance": "IndiaScene365 (Mendeley Data CC BY 4.0)"
        },
        {
            "key": "sample_urban_arterial",
            "name": "Verified Indian Highway / Arterial (IndiaScene365)",
            "category": "not_waterlogged",
            "expected_label": "not_waterlogged",
            "description": "Multi-lane roadway with normal traffic and zero standing water puddles.",
            "url": "/static/samples/sample_urban_arterial.png",
            "provenance": "IndiaScene365 (Mendeley Data CC BY 4.0)"
        },
        {
            "key": "sample_rainy_wet_road",
            "name": "Verified Wet Rainy Road without Flooding (IndiaScene365)",
            "category": "not_waterlogged",
            "expected_label": "not_waterlogged",
            "description": "Damp asphalt during overcast conditions without standing pools or flooding.",
            "url": "/static/samples/sample_rainy_wet_road.png",
            "provenance": "IndiaScene365 (Mendeley Data CC BY 4.0)"
        }
    ]


@router.post("/detection/sample-detect")
def detect_sample_image(payload: SampleDetectionRequest):
    """Runs inference directly on a pre-verified sample image."""
    sample_map = {
        "sample_waterlogged": SAMPLES_DIR / "sample_waterlogged.jpg",
        "sample_dry_road": SAMPLES_DIR / "sample_dry_road.png",
        "sample_urban_arterial": SAMPLES_DIR / "sample_urban_arterial.png",
        "sample_rainy_wet_road": SAMPLES_DIR / "sample_rainy_wet_road.png"
    }

    target_file = sample_map.get(payload.sample_key)
    if not target_file or not target_file.exists():
        raise HTTPException(status_code=404, detail=f"Sample '{payload.sample_key}' not found.")

    try:
        results = image_adapter.detect(target_file, conf_threshold=payload.conf_threshold)
        results["image_url"] = f"/static/samples/{target_file.name}"
        results["is_sample"] = True
        results["sample_key"] = payload.sample_key
        return results
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Sample inference failed: {str(e)}")


@router.post("/detection/image")
async def detect_waterlogging_in_image(
    image: UploadFile = File(...),
    conf_threshold: float = Form(0.25)
):
    """
    Runs optical waterlogging detection on an uploaded roadway image using YOLOv11 and MobileNetV3.
    """
    if not image_adapter.is_available():
        raise HTTPException(
            status_code=503,
            detail="Image detection model is not available. Ensure models/image/best.pt exists."
        )

    # Validate file extension
    ext = image.filename.split(".")[-1].lower() if "." in image.filename else ""
    if ext not in ["jpg", "jpeg", "png", "webp"]:
        raise HTTPException(status_code=400, detail="Only JPG, JPEG, PNG, and WEBP formats are accepted.")

    # Save to uploads directory
    saved_filename = f"detect_{uuid.uuid4().hex[:10]}.{ext}"
    dest_path = UPLOADS_DIR / saved_filename

    contents = await image.read()
    if len(contents) > 10 * 1024 * 1024:
        raise HTTPException(status_code=400, detail="Image size exceeds 10 MB limit.")

    with open(dest_path, "wb") as f:
        f.write(contents)

    try:
        results = image_adapter.detect(dest_path, conf_threshold=conf_threshold)
        results["image_url"] = f"/api/v1/uploads/{saved_filename}"
        results["is_sample"] = False
        return results
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Image inference failed: {str(e)}")
