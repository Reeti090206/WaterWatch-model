"""
WaterWatch AI Integration - Read-Only Image Detection Model Adapter
Loads YOLOv11 detector (models/image/best.pt) without modifying existing model weights.
"""

from typing import Dict, Any, List
from pathlib import Path
from PIL import Image
from waterwatch_integration.backend.app.config import IMAGE_MODEL_PATH


class ImageDetectionAdapter:
    """Read-only adapter for the trained YOLOv11 waterlogging detector."""

    def __init__(self):
        self._model = None
        self._model_path = None
        self._load_model()

    def _load_model(self):
        if IMAGE_MODEL_PATH.exists():
            try:
                from ultralytics import YOLO
                self._model = YOLO(str(IMAGE_MODEL_PATH))
                self._model_path = IMAGE_MODEL_PATH
            except Exception as e:
                self._model = None
                self._load_error = str(e)
        else:
            self._model = None
            self._load_error = f"Image weights not found at {IMAGE_MODEL_PATH}"

    def is_available(self) -> bool:
        return self._model is not None

    def get_status(self) -> Dict[str, Any]:
        return {
            "model_type": "Ultralytics YOLOv11 Nano (yolo11n)",
            "artifact_path": str(self._model_path) if self._model_path else str(IMAGE_MODEL_PATH),
            "is_available": self.is_available(),
            "target_class": "water_logging",
            "readiness": "EXPERIMENTAL (Optical Surface Detection)",
            "limitations": "Detects visible puddle/water pooling surfaces. Cannot measure depth in cm without physical gauges."
        }

    def detect(self, image_path: Path, conf_threshold: float = 0.25) -> Dict[str, Any]:
        """
        Runs read-only YOLO inference on an uploaded image file.
        """
        if not self.is_available():
            raise RuntimeError(f"Image detection model is not available: {getattr(self, '_load_error', 'Not loaded')}")

        if not image_path.exists():
            raise FileNotFoundError(f"Image file not found: {image_path}")

        # Validate that image is openable
        try:
            with Image.open(image_path) as img:
                img_width, img_height = img.size
        except Exception as e:
            raise ValueError(f"Invalid image format: {str(e)}")

        results = self._model.predict(
            source=str(image_path),
            conf=conf_threshold,
            save=False,
            verbose=False
        )

        detections = []
        if results and len(results) > 0:
            boxes = results[0].boxes
            for box in boxes:
                xyxy = box.xyxy[0].tolist()
                conf = round(float(box.conf[0]), 4)
                cls_id = int(box.cls[0])
                cls_name = self._model.names.get(cls_id, "water_logging")
                detections.append({
                    "class_id": cls_id,
                    "class_name": cls_name,
                    "confidence": conf,
                    "bbox_pixels": [round(c, 1) for c in xyxy],
                    "bbox_normalized": [
                        round(xyxy[0] / img_width, 4),
                        round(xyxy[1] / img_height, 4),
                        round(xyxy[2] / img_width, 4),
                        round(xyxy[3] / img_height, 4)
                    ]
                })

        waterlogging_detected = len(detections) > 0

        return {
            "image_filename": image_path.name,
            "dimensions": {"width": img_width, "height": img_height},
            "waterlogging_detected": waterlogging_detected,
            "detection_count": len(detections),
            "detections": detections,
            "conf_threshold_used": conf_threshold,
            "disclaimer": (
                "Visual detection indicates surface water reflection/pooling. "
                "2D bounding boxes do not represent physical depth in centimeters."
            )
        }


# Singleton instance
image_adapter = ImageDetectionAdapter()
