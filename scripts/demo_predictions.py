"""WaterWatch AI - Prediction Model Demo"""

import sys, json
sys.path.insert(0, 'scripts')
import joblib
import pandas as pd
import numpy as np
from rainfall_model_utils import ExperimentalMeteorologicalRiskBaseline, FEATURE_COLUMNS
from pathlib import Path

# ─── RAINFALL RISK PREDICTION ─────────────────────────────────────────────────
model = joblib.load('models/rainfall/experimental_risk_baseline.joblib')

scenarios = [
    {'name': 'Dry Day',                         'rainfall_mm': 2.0,   'rainfall_prev1_day_mm': 0.5,   'rainfall_prev2_day_mm': 0.0,  'rainfall_2day_total_mm': 2.5,   'rainfall_3day_total_mm': 2.5,   'api_7day': 5.0,   'rainfall_trend_ratio': 0.8,  'is_monsoon': 0},
    {'name': 'Light Shower',                    'rainfall_mm': 8.0,   'rainfall_prev1_day_mm': 3.0,   'rainfall_prev2_day_mm': 1.0,  'rainfall_2day_total_mm': 11.0,  'rainfall_3day_total_mm': 12.0,  'api_7day': 12.0,  'rainfall_trend_ratio': 0.67, 'is_monsoon': 1},
    {'name': 'Moderate Shower',                 'rainfall_mm': 32.0,  'rainfall_prev1_day_mm': 15.0,  'rainfall_prev2_day_mm': 8.0,  'rainfall_2day_total_mm': 47.0,  'rainfall_3day_total_mm': 55.0,  'api_7day': 38.0,  'rainfall_trend_ratio': 0.58, 'is_monsoon': 1},
    {'name': 'Heavy Rain',                      'rainfall_mm': 80.0,  'rainfall_prev1_day_mm': 45.0,  'rainfall_prev2_day_mm': 30.0, 'rainfall_2day_total_mm': 125.0, 'rainfall_3day_total_mm': 155.0, 'api_7day': 85.0,  'rainfall_trend_ratio': 0.52, 'is_monsoon': 1},
    {'name': 'Very Heavy + Saturated Soil',     'rainfall_mm': 130.0, 'rainfall_prev1_day_mm': 90.0,  'rainfall_prev2_day_mm': 60.0, 'rainfall_2day_total_mm': 220.0, 'rainfall_3day_total_mm': 280.0, 'api_7day': 110.0, 'rainfall_trend_ratio': 0.46, 'is_monsoon': 1},
    {'name': 'Extreme / Cloudburst',            'rainfall_mm': 220.0, 'rainfall_prev1_day_mm': 140.0, 'rainfall_prev2_day_mm': 85.0, 'rainfall_2day_total_mm': 360.0, 'rainfall_3day_total_mm': 445.0, 'api_7day': 130.0, 'rainfall_trend_ratio': 0.49, 'is_monsoon': 1},
    {'name': 'Nagpur - Kamtheekhairi (Jul)',    'rainfall_mm': 64.0,  'rainfall_prev1_day_mm': 18.0,  'rainfall_prev2_day_mm': 42.0, 'rainfall_2day_total_mm': 82.0,  'rainfall_3day_total_mm': 124.0, 'api_7day': 78.0,  'rainfall_trend_ratio': 0.52, 'is_monsoon': 1},
    {'name': 'Nagpur - Kuhi Station (Aug)',     'rainfall_mm': 92.0,  'rainfall_prev1_day_mm': 55.0,  'rainfall_prev2_day_mm': 38.0, 'rainfall_2day_total_mm': 147.0, 'rainfall_3day_total_mm': 185.0, 'api_7day': 102.0, 'rainfall_trend_ratio': 0.50, 'is_monsoon': 1},
]

print()
print("=" * 76)
print("   WATERWATCH AI  |  RAINFALL RISK PREDICTION MODEL")
print("   Region: Maharashtra, India (Nagpur Focus)")
print("   Model: ExperimentalMeteorologicalRiskBaseline (Physics-based Heuristic)")
print("=" * 76)
print()
print(f"  {'Scenario':<38} {'Rain (mm)':<11} {'API-7d':<8} {'Score':<8} {'Risk Level'}")
print("  " + "-" * 74)

for s in scenarios:
    X = pd.DataFrame([s])
    score = model.predict_risk(X[FEATURE_COLUMNS])[0]
    if score < 0.20:   level = "LOW          "
    elif score < 0.45: level = "MODERATE     "
    elif score < 0.70: level = "HIGH      !"
    else:              level = "CRITICAL  !!"

    bar_len = int(score * 20)
    bar = "[" + "#" * bar_len + "." * (20 - bar_len) + "]"
    print(f"  {s['name']:<38} {s['rainfall_mm']:<11.1f} {s['api_7day']:<8.1f} {score:<8.4f} {level}")

print()
print("  Risk Scale: 0.0 = No Risk  |  0.45 = Moderate  |  0.70+ = Critical")
print()
print("  IMD Categories Calibrated:")
print("    Very Light (<2.5mm)  Light (<15.5mm)  Moderate (<64.5mm)")
print("    Heavy (<115.5mm)     Very Heavy (<204.5mm)  Extremely Heavy (200mm+)")
print()
print("  7-day API Formula: API_t = sum(0.85^k * R_{t-k})  — decay=0.85")
print()
print("  DISCLAIMER: Experimental heuristic. No ground-truth event labels exist yet.")
print("  To train a supervised model: provide verified municipal waterlogging logs")
print("  to scripts/build_event_dataset.py then re-run train_rainfall_model.py")
print("=" * 76)

# ─── IMAGE DETECTION PREDICTION ───────────────────────────────────────────────
print()
print("=" * 76)
print("   WATERWATCH AI  |  VISUAL WATERLOGGING DETECTION (YOLOv11)")
print("   Model: yolo11n  |  Weights: models/image/best.pt")
print("=" * 76)
print()

from predict_image import predict
test_img_dir = Path("data/processed/yolo_water_logging/images/test")
test_images = sorted(test_img_dir.glob("*.jpg"))[:8]

detections_found = 0
for img_path in test_images:
    result = predict(source_path=img_path, conf_thresh=0.20)[0]
    detected = result["waterlogging_detected"]
    n = result["detection_count"]
    if detected:
        detections_found += 1
        best_conf = max(d["confidence"] for d in result["detections"]) if result["detections"] else 0.0
        print(f"  DETECTED   {img_path.name[:52]:<52} [{n} box(es), conf={best_conf:.2f}]")
    else:
        print(f"  no detect  {img_path.name[:52]:<52}")

print()
print(f"  Sample: {len(test_images)} images | Detections: {detections_found}")
print()
print("  Held-Out Test Evaluation (21 images, 46 instances):")
import json
with open("reports/image_model_evaluation.json") as f:
    ev = json.load(f)
print(f"    Precision : {ev['precision']}")
print(f"    Recall    : {ev['recall']}")
print(f"    mAP@0.50  : {ev['mAP50']}")
print(f"    mAP@50-95 : {ev['mAP50_95']}")
print()
print("  NOTE: Low mAP is expected — only 3 epochs on 139 CPU-trained images.")
print("  Run: python scripts/train_image_model.py --epochs 30 --batch 16")
print("  for significantly improved detection performance.")
print("=" * 76)
