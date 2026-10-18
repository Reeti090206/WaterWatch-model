"""
WaterWatch AI - Image Model Evaluation Engine
Evaluates YOLOv11 waterlogging detection performance on the held-out test split,
computing Precision, Recall, mAP50, and mAP50-95.
"""

import os
import sys
import argparse
import json
from pathlib import Path
from ultralytics import YOLO

PROJECT_ROOT = Path(__file__).resolve().parent.parent
DATA_DIR = PROJECT_ROOT / "data"
MODELS_DIR = PROJECT_ROOT / "models" / "image"
REPORTS_DIR = PROJECT_ROOT / "reports"
DATA_YAML = DATA_DIR / "processed" / "yolo_water_logging" / "data.yaml"

REPORTS_DIR.mkdir(parents=True, exist_ok=True)


def evaluate(weights_path=None, split="test", imgsz=640, device="cpu"):
    print("=" * 60)
    print("EVALUATING YOLOV11 WATERLOGGING DETECTION MODEL")
    print(f"Target Split: {split.upper()}")
    print("=" * 60)

    if weights_path is None:
        target_pt = MODELS_DIR / "best.pt"
        if not target_pt.exists():
            print("Notice: models/image/best.pt not yet trained. Using pretrained yolo11n.pt as baseline evaluation.")
            target_pt = "yolo11n.pt"
    else:
        target_pt = Path(weights_path)

    print(f"Model weights: {target_pt}")
    model = YOLO(str(target_pt))

    metrics = model.val(
        data=str(DATA_YAML).replace("\\", "/"),
        split=split,
        imgsz=imgsz,
        device=device,
        project=str(PROJECT_ROOT / "runs" / "val").replace("\\", "/"),
        name="water_logging_eval",
        exist_ok=True,
        verbose=True
    )

    results = {
        "model_weights": str(target_pt),
        "split_evaluated": split,
        "precision": round(float(metrics.box.mp), 4) if hasattr(metrics.box, "mp") else None,
        "recall": round(float(metrics.box.mr), 4) if hasattr(metrics.box, "mr") else None,
        "mAP50": round(float(metrics.box.map50), 4) if hasattr(metrics.box, "map50") else None,
        "mAP50_95": round(float(metrics.box.map), 4) if hasattr(metrics.box, "map") else None
    }

    print("\n--- Held-Out Test Evaluation Results ---")
    print(f"Precision: {results['precision']}")
    print(f"Recall:    {results['recall']}")
    print(f"mAP@0.50:  {results['mAP50']}")
    print(f"mAP@50-95: {results['mAP50_95']}")

    out_json = REPORTS_DIR / "image_model_evaluation.json"
    with open(out_json, "w", encoding="utf-8") as f:
        json.dump(results, f, indent=2)
    print(f"\nSaved evaluation metrics to {out_json}")
    return results


def main():
    parser = argparse.ArgumentParser(description="WaterWatch Image Model Evaluation")
    parser.add_argument("--weights", type=str, default=None, help="Path to model weights (.pt)")
    parser.add_argument("--split", type=str, default="test", help="Split to evaluate ('test', 'val')")
    parser.add_argument("--imgsz", type=int, default=640, help="Image size")
    parser.add_argument("--device", type=str, default="cpu", help="Device ('cpu', '0')")
    args = parser.parse_args()

    evaluate(args.weights, args.split, args.imgsz, args.device)


if __name__ == "__main__":
    main()
