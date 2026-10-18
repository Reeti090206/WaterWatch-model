"""
WaterWatch AI - Standalone Image Inference Engine
Runs inference on single images or directories using the trained YOLOv11 detector,
returning structured JSON bounding boxes, confidence scores, and detection flags.
"""

import os
import sys
import argparse
import json
from pathlib import Path
from ultralytics import YOLO

PROJECT_ROOT = Path(__file__).resolve().parent.parent
MODELS_DIR = PROJECT_ROOT / "models" / "image"
RUNS_DIR = PROJECT_ROOT / "runs" / "predict"


def predict(source_path, weights_path=None, conf_thresh=0.25, save_annotated=False, output_dir=None):
    if weights_path is None:
        target_pt = MODELS_DIR / "best.pt"
        if not target_pt.exists():
            print("Notice: models/image/best.pt not found. Using pretrained yolo11n.pt weights.")
            target_pt = "yolo11n.pt"
    else:
        target_pt = Path(weights_path)

    model = YOLO(str(target_pt))

    source_path = Path(source_path)
    if not source_path.exists():
        raise FileNotFoundError(f"Input source not found: {source_path}")

    save_dir = Path(output_dir) if output_dir else RUNS_DIR
    save_dir.mkdir(parents=True, exist_ok=True)

    results = model.predict(
        source=str(source_path),
        conf=conf_thresh,
        save=save_annotated,
        project=str(save_dir.parent).replace("\\", "/"),
        name=save_dir.name,
        exist_ok=True,
        verbose=False
    )

    outputs = []
    for r in results:
        img_file = r.path
        boxes = r.boxes
        detections = []
        
        if boxes is not None and len(boxes) > 0:
            for b in boxes:
                xyxy = [round(float(coord), 2) for coord in b.xyxy[0].tolist()]
                xywhn = [round(float(coord), 4) for coord in b.xywhn[0].tolist()]
                conf = round(float(b.conf[0]), 4)
                cls_id = int(b.cls[0])
                cls_name = model.names.get(cls_id, f"class_{cls_id}")

                detections.append({
                    "class_id": cls_id,
                    "class_name": cls_name,
                    "confidence": conf,
                    "bbox_xyxy": xyxy,
                    "bbox_normalized_xywh": xywhn
                })

        item_result = {
            "image_path": str(img_file),
            "waterlogging_detected": len(detections) > 0,
            "detection_count": len(detections),
            "detections": detections,
            "scientific_disclaimer": "Visual appearance only. Do not infer precise rainfall, capture time, GPS coordinates, or water depth from image appearance alone."
        }
        outputs.append(item_result)

    return outputs


def main():
    parser = argparse.ArgumentParser(description="WaterWatch Image Inference")
    parser.add_argument("--source", type=str, required=True, help="Path to input image file or directory")
    parser.add_argument("--weights", type=str, default=None, help="Path to YOLO weights (.pt)")
    parser.add_argument("--conf", type=float, default=0.25, help="Confidence threshold")
    parser.add_argument("--save", action="store_true", help="Save annotated detection image")
    parser.add_argument("--output_dir", type=str, default=None, help="Output directory for annotated images")
    args = parser.parse_args()

    results = predict(
        source_path=args.source,
        weights_path=args.weights,
        conf_thresh=args.conf,
        save_annotated=args.save,
        output_dir=args.output_dir
    )

    print(json.dumps(results, indent=2))


if __name__ == "__main__":
    main()
