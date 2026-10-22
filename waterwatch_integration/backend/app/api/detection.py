"""
WaterWatch AI Integration - Image Detection API Router
"""

import uuid
from pathlib import Path
from fastapi import APIRouter, UploadFile, File, HTTPException, Form
from waterwatch_integration.backend.app.config import UPLOADS_DIR
from waterwatch_integration.backend.app.adapters.image_adapter import image_adapter

router = APIRouter(tags=["Image Detection"])


@router.post("/detection/image")
async def detect_waterlogging_in_image(
    image: UploadFile = File(...),
    conf_threshold: float = Form(0.25)
):
    """
    Runs optical waterlogging detection on an uploaded roadway image using YOLOv11.
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
        return results
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Image inference failed: {str(e)}")
