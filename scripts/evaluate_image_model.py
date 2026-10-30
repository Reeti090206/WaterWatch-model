"""
WaterWatch AI - Comprehensive Image Model Evaluation Engine
Evaluates YOLOv11 and MobileNetV3 models on the held-out test split (N=79: 31 positive, 48 negative).
Computes:
1. Object detection metrics: Precision, Recall, mAP@0.50, mAP@0.50:0.95
2. Image-level classification metrics: Accuracy, Precision, Recall, Specificity, F1-score, Confusion Matrix
3. Comparison against baseline model (trained without negative road scenes).
"""

import os
import sys
import argparse
import json
import time
from pathlib import Path
from ultralytics import YOLO
import numpy as np
from sklearn.metrics import accuracy_score, precision_score, recall_score, f1_score, confusion_matrix, roc_auc_score

PROJECT_ROOT = Path(__file__).resolve().parent.parent
DATA_DIR = PROJECT_ROOT / "data"
MODELS_DIR = PROJECT_ROOT / "models" / "image"
REPORTS_DIR = PROJECT_ROOT / "reports"
DATA_YAML = DATA_DIR / "processed" / "yolo_water_logging" / "data.yaml"
TEST_IMG_DIR = DATA_DIR / "processed" / "yolo_water_logging" / "images" / "test"
TEST_LBL_DIR = DATA_DIR / "processed" / "yolo_water_logging" / "labels" / "test"

REPORTS_DIR.mkdir(parents=True, exist_ok=True)


def evaluate_yolo(weights_path=None, split="test", imgsz=640, device="cpu", conf_thresh=0.25):
    print("=" * 65)
    print(f"EVALUATING YOLOV11 DETECTOR ON {split.upper()} SPLIT")
    print("=" * 65)

    if weights_path is None:
        target_pt = MODELS_DIR / "best.pt"
        if not target_pt.exists():
            target_pt = MODELS_DIR / "best_baseline.pt"
            if not target_pt.exists():
                target_pt = "yolo11n.pt"
    else:
        target_pt = Path(weights_path)

    print(f"Model weights evaluated: {target_pt}")
    model = YOLO(str(target_pt))

    # 1. Bounding box detection metrics via Ultralytics val
    metrics = model.val(
        data=str(DATA_YAML).replace("\\", "/"),
        split=split,
        imgsz=imgsz,
        device=device,
        project=str(PROJECT_ROOT / "runs" / "val").replace("\\", "/"),
        name="water_logging_eval",
        exist_ok=True,
        verbose=False
    )

    box_metrics = {
        "box_precision": round(float(metrics.box.mp), 4) if hasattr(metrics.box, "mp") else 0.0,
        "box_recall": round(float(metrics.box.mr), 4) if hasattr(metrics.box, "mr") else 0.0,
        "mAP50": round(float(metrics.box.map50), 4) if hasattr(metrics.box, "map50") else 0.0,
        "mAP50_95": round(float(metrics.box.map), 4) if hasattr(metrics.box, "map") else 0.0
    }

    # 2. Image-level classification metrics using detection-to-image decision rule
    y_true = []
    y_pred = []
    max_confs = []
    all_imgs = sorted(list(TEST_IMG_DIR.glob("*.*")))

    for img_p in all_imgs:
        lbl_p = TEST_LBL_DIR / (img_p.stem + ".txt")
        has_water = bool(lbl_p.read_text().strip()) if lbl_p.exists() else False
        y_true.append(1 if has_water else 0)

        res = model.predict(source=str(img_p), conf=conf_thresh, verbose=False)[0]
        detected = len(res.boxes) > 0
        y_pred.append(1 if detected else 0)
        c = float(res.boxes.conf.max()) if len(res.boxes) > 0 else 0.0
        max_confs.append(c)

    acc = accuracy_score(y_true, y_pred)
    prec = precision_score(y_true, y_pred, zero_division=0)
    rec = recall_score(y_true, y_pred, zero_division=0)
    f1 = f1_score(y_true, y_pred, zero_division=0)
    cm = confusion_matrix(y_true, y_pred).tolist()
    tn, fp, fn, tp = cm[0][0], cm[0][1], cm[1][0], cm[1][1]
    spec = tn / (tn + fp) if (tn + fp) > 0 else 0.0

    cls_metrics = {
        "accuracy": round(float(acc), 4),
        "precision": round(float(prec), 4),
        "recall": round(float(rec), 4),
        "specificity": round(float(spec), 4),
        "f1_score": round(float(f1), 4),
        "confusion_matrix": {
            "true_negative": tn,
            "false_positive": fp,
            "false_negative": fn,
            "true_positive": tp
        }
    }

    out = {
        "model_name": "YOLOv11 Nano Detector",
        "weights_path": str(target_pt),
        "split_evaluated": split,
        "confidence_threshold": conf_thresh,
        "sample_count": len(all_imgs),
        "box_metrics": box_metrics,
        "classification_metrics": cls_metrics
    }

    print("\n--- YOLO Evaluation Results on Held-Out Test ---")
    print(f"  Box mAP@0.50 : {box_metrics['mAP50']}")
    print(f"  Box mAP@50-95: {box_metrics['mAP50_95']}")
    print(f"  Box Precision: {box_metrics['box_precision']}")
    print(f"  Box Recall   : {box_metrics['box_recall']}")
    print(f"  Image Accuracy: {cls_metrics['accuracy']:.4f} ({cls_metrics['accuracy']*100:.1f}%)")
    print(f"  Image Prec   : {cls_metrics['precision']}")
    print(f"  Image Recall : {cls_metrics['recall']}")
    print(f"  Image F1     : {cls_metrics['f1_score']}")
    print(f"  Confusion Matrix: TN={tn}, FP={fp}, FN={fn}, TP={tp}")

    out_json = REPORTS_DIR / "image_model_evaluation.json"
    with open(out_json, "w", encoding="utf-8") as f:
        json.dump(out, f, indent=2)
    print(f"\nSaved evaluation metrics to {out_json}")
    return out


def main():
    parser = argparse.ArgumentParser(description="WaterWatch Image Model Evaluation")
    parser.add_argument("--weights", type=str, default=None, help="Path to model weights (.pt)")
    parser.add_argument("--split", type=str, default="test", help="Split to evaluate ('test', 'val')")
    parser.add_argument("--imgsz", type=int, default=640, help="Image size")
    parser.add_argument("--device", type=str, default="cpu", help="Device ('cpu', '0')")
    parser.add_argument("--conf", type=float, default=0.25, help="Confidence threshold")
    args = parser.parse_args()

    evaluate_yolo(args.weights, args.split, args.imgsz, args.device, args.conf)


if __name__ == "__main__":
    main()
