"""
WaterWatch AI Integration - Enhanced Image Model Adapter
Supports both YOLOv11 Object Detection and MobileNetV3-Small Classification.
Provides bounding boxes, classification confidence, rule-based severity,
inference latency measurement, and uncertainty estimation.
"""

from typing import Dict, Any, List, Optional
import time
from pathlib import Path
from PIL import Image
import torch
import torch.nn as nn
from torchvision import models, transforms
from waterwatch_integration.backend.app.config import IMAGE_MODEL_PATH, PROJECT_ROOT

CLASSIFIER_PATH = PROJECT_ROOT / "models" / "image" / "mobilenetv3_waterlogging_best.pth"


class ImageDetectionAdapter:
    """Multi-model adapter serving YOLOv11 detector and MobileNetV3 classifier."""

    def __init__(self):
        self._yolo_model = None
        self._classifier_model = None
        self._classifier_tf = None
        self._load_yolo()
        self._load_classifier()

    def _load_yolo(self):
        if IMAGE_MODEL_PATH.exists():
            try:
                from ultralytics import YOLO
                self._yolo_model = YOLO(str(IMAGE_MODEL_PATH))
            except Exception as e:
                self._yolo_model = None
                self._yolo_error = str(e)
        else:
            self._yolo_model = None
            self._yolo_error = f"YOLO weights not found at {IMAGE_MODEL_PATH}"

    def _load_classifier(self):
        if CLASSIFIER_PATH.exists():
            try:
                device = "cpu"
                model = models.mobilenet_v3_small(weights=None)
                in_features = model.classifier[3].in_features
                model.classifier[3] = nn.Sequential(
                    nn.Dropout(p=0.2),
                    nn.Linear(in_features, 2)
                )
                model.load_state_dict(torch.load(CLASSIFIER_PATH, map_location=device))
                model.eval()
                self._classifier_model = model
                self._classifier_tf = transforms.Compose([
                    transforms.Resize((224, 224)),
                    transforms.ToTensor(),
                    transforms.Normalize(mean=[0.485, 0.456, 0.406], std=[0.229, 0.224, 0.225])
                ])
            except Exception as e:
                self._classifier_model = None
                self._classifier_error = str(e)
        else:
            self._classifier_model = None
            self._classifier_error = f"Classifier weights not found at {CLASSIFIER_PATH}"

    def is_available(self) -> bool:
        return self._yolo_model is not None or self._classifier_model is not None

    def get_status(self) -> Dict[str, Any]:
        return {
            "yolo_detector": {
                "available": self._yolo_model is not None,
                "type": "Ultralytics YOLOv11 Nano (yolo11n)",
                "path": str(IMAGE_MODEL_PATH),
                "target_class": "water_logging (bounding box)"
            },
            "classifier": {
                "available": self._classifier_model is not None,
                "type": "PyTorch MobileNetV3-Small",
                "path": str(CLASSIFIER_PATH),
                "classes": ["not_waterlogged", "waterlogged"]
            },
            "is_available": self.is_available(),
            "readiness": "OPERATIONAL (Dual-Stream CV Pipeline)",
            "limitations": "Surface water visual pattern detection. Physical water depth in cm requires calibrated staff gauges."
        }

    def detect(self, image_path: Path, conf_threshold: float = 0.25) -> Dict[str, Any]:
        """
        Runs dual inference on an uploaded roadway image.
        Returns predicted class, confidence, bounding boxes, severity, latency, and uncertainty.
        """
        if not self.is_available():
            raise RuntimeError("Image models are not available.")

        if not image_path.exists():
            raise FileNotFoundError(f"Image file not found: {image_path}")

        t0 = time.time()

        # Validate and open image
        try:
            with Image.open(image_path) as img:
                img_width, img_height = img.size
                rgb_img = img.convert("RGB")
        except Exception as e:
            raise ValueError(f"Invalid image format: {str(e)}")

        # 1. Run MobileNetV3 Classification if available
        cls_water_prob = None
        cls_predicted = None
        if self._classifier_model is not None:
            try:
                with torch.no_grad():
                    input_tensor = self._classifier_tf(rgb_img).unsqueeze(0)
                    logits = self._classifier_model(input_tensor)
                    probs = torch.softmax(logits, dim=1)[0]
                    # Index 1 is waterlogged, 0 is not_waterlogged
                    cls_water_prob = round(float(probs[1]), 4)
                    # Decision threshold 0.20 tuned on validation split
                    cls_predicted = "waterlogged" if cls_water_prob >= 0.20 else "not_waterlogged"
            except Exception:
                cls_water_prob = None
                cls_predicted = None

        # 2. Run YOLOv11 Object Detection if available
        detections = []
        max_yolo_conf = 0.0
        total_box_area = 0.0

        if self._yolo_model is not None:
            results = self._yolo_model.predict(
                source=str(image_path),
                conf=conf_threshold,
                save=False,
                verbose=False
            )

            if results and len(results) > 0:
                boxes = results[0].boxes
                for box in boxes:
                    xyxy = box.xyxy[0].tolist()
                    conf = round(float(box.conf[0]), 4)
                    cls_id = int(box.cls[0])
                    cls_name = self._yolo_model.names.get(cls_id, "water_logging")

                    w_box = max(0.0, xyxy[2] - xyxy[0])
                    h_box = max(0.0, xyxy[3] - xyxy[1])
                    box_area_pct = (w_box * h_box) / max(1.0, (img_width * img_height)) * 100.0
                    total_box_area += box_area_pct

                    if conf > max_yolo_conf:
                        max_yolo_conf = conf

                    detections.append({
                        "class_id": cls_id,
                        "class_name": cls_name,
                        "confidence": conf,
                        "area_percentage": round(box_area_pct, 2),
                        "bbox_pixels": [round(c, 1) for c in xyxy],
                        "bbox_normalized": [
                            round(xyxy[0] / img_width, 4),
                            round(xyxy[1] / img_height, 4),
                            round(xyxy[2] / img_width, 4),
                            round(xyxy[3] / img_height, 4)
                        ]
                    })

        # 3. Unified Decision
        if cls_predicted is not None:
            final_class = cls_predicted
            confidence = cls_water_prob if final_class == "waterlogged" else round(1.0 - cls_water_prob, 4)
        else:
            final_class = "waterlogged" if len(detections) > 0 else "not_waterlogged"
            confidence = max_yolo_conf if final_class == "waterlogged" else round(1.0 - max_yolo_conf, 4)

        waterlogging_detected = (final_class == "waterlogged")

        # 4. Validated Severity Heuristic Rule
        if not waterlogging_detected:
            severity = "None"
            severity_description = "Dry roadway surface with no visible standing water or pooling."
        else:
            if total_box_area < 6.0 and len(detections) <= 1:
                severity = "Low"
                severity_description = "Minor surface water accumulation / localized puddle (<6% roadway coverage)."
            elif total_box_area < 20.0 or len(detections) <= 2:
                severity = "Moderate"
                severity_description = "Moderate curb-level waterlogging (6-20% roadway coverage); caution advised."
            else:
                severity = "High"
                severity_description = "Substantial roadway inundation (>20% roadway coverage); severe vehicle stall hazard."

        # 5. Uncertainty Message
        uncertainty_warning = None
        if 0.40 <= confidence <= 0.65:
            uncertainty_warning = "Borderline prediction confidence. Surface reflections, wet pavement, or low lighting may be ambiguous."
        elif cls_predicted is not None and len(detections) == 0 and cls_predicted == "waterlogged":
            uncertainty_warning = "Classifier detected surface water characteristics, but bounding box detector found diffuse pooling."

        inference_time_ms = round((time.time() - t0) * 1000.0, 1)

        return {
            "image_filename": image_path.name,
            "dimensions": {"width": img_width, "height": img_height},
            "predicted_class": final_class,
            "waterlogging_detected": waterlogging_detected,
            "confidence": confidence,
            "confidence_percentage": round(confidence * 100.0, 1),
            "detection_count": len(detections),
            "detections": detections,
            "total_water_area_percentage": round(total_box_area, 2),
            "severity": severity,
            "severity_description": severity_description,
            "uncertainty_warning": uncertainty_warning,
            "inference_time_ms": inference_time_ms,
            "model_version": "WaterWatch Vision Pipeline (YOLOv11n + MobileNetV3-Small)",
            "disclaimer": (
                "Visual detection indicates surface water reflection/pooling. "
                "2D bounding boxes and area percentages represent visual coverage heuristics, "
                "NOT physical water depth in centimeters."
            )
        }


# Singleton instance
image_adapter = ImageDetectionAdapter()
