"""
WaterWatch AI - Combined Prediction & Visual Verification Pipeline
Orchestrates dual-modality assessment:
  1. Rainfall-based waterlogging risk prediction (hydrometeorological hazard)
  2. Image-based visual detection (optical ground verification)
Maintains strict separation between models and flags signal disagreement for human operator review.
"""

import os
import sys
import json
import argparse
from pathlib import Path
from datetime import datetime

PROJECT_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(Path(__file__).resolve().parent))

from predict_rainfall import predict_rainfall
from predict_image import predict as predict_image_fn


def run_combined_pipeline(
    rainfall_mm,
    image_path,
    location="Nagpur",
    prev1_mm=0.0,
    prev2_mm=0.0,
    api_7day=None,
    conf_thresh=0.25,
    save_annotated=False,
    output_dir="runs/combined"
):
    """
    Executes independent rainfall risk inference and image detection,
    then evaluates agreement/disagreement without arbitrary score blending.
    """
    now = datetime.now()

    # 1. Rainfall Inference
    rainfall_res = predict_rainfall(
        rainfall_mm=rainfall_mm,
        prev1_mm=prev1_mm,
        prev2_mm=prev2_mm,
        api_7day=api_7day,
        location=location
    )

    # 2. Image Inference
    image_file = Path(image_path)
    if not image_file.exists():
        raise FileNotFoundError(f"Input image not found: {image_file}")

    image_res = predict_image_fn(
        source_path=image_file,
        conf_thresh=conf_thresh,
        save_annotated=save_annotated,
        output_dir=output_dir
    )[0]

    # 3. Disagreement & Verification Logic
    rain_score = rainfall_res["waterlogging_risk_score"]
    rain_high = rain_score >= 0.45
    rain_low = rain_score < 0.20

    img_detected = image_res["waterlogging_detected"]
    box_count = image_res["detection_count"]

    if rain_high and img_detected:
        consensus_status = "CONFIRMED_HAZARD"
        consensus_summary = "High precipitation and visible road waterlogging mutually confirmed."
        flag_for_review = False
    elif rain_low and not img_detected:
        consensus_status = "CONFIRMED_CLEAR"
        consensus_summary = "Low meteorological precipitation and dry roadway visually confirmed."
        flag_for_review = False
    elif rain_high and not img_detected:
        consensus_status = "DISAGREEMENT_PRECIPITATION_AHEAD"
        consensus_summary = (
            "High hydrometeorological risk, but NO visual waterlogging detected in camera frame. "
            "Operator Review: verify local drainage clearance, camera blind spots, or drainage time-lag."
        )
        flag_for_review = True
    elif rain_low and img_detected:
        consensus_status = "DISAGREEMENT_OPTICAL_ANOMALY"
        consensus_summary = (
            "Visual waterlogging detected despite low recorded rainfall. "
            "Operator Review: check for blocked stormwater drain, water main rupture, or upstream canal discharge."
        )
        flag_for_review = True
    else:
        consensus_status = "MODERATE_OR_UNCERTAIN"
        consensus_summary = "Moderate rainfall or partial pooling conditions. Standard monitoring advised."
        flag_for_review = False

    combined_output = {
        "execution_timestamp": now.isoformat(),
        "location": location,
        "rainfall_component": {
            "model_type": rainfall_res["model_architecture"],
            "is_supervised": rainfall_res["is_supervised_trained"],
            "current_rainfall_mm": rainfall_res["features"]["rainfall_mm"],
            "imd_category": rainfall_res["imd_category"],
            "api_7day": rainfall_res["features"]["api_7day"],
            "rainfall_risk_score": rain_score,
            "risk_level": rainfall_res["risk_level"]
        },
        "image_component": {
            "image_path": str(image_file),
            "model_architecture": "YOLOv11n Object Detector (water_logging)",
            "waterlogging_detected": img_detected,
            "detection_count": box_count,
            "detections": image_res["detections"],
            "annotated_image_path": image_res.get("saved_annotated_path")
        },
        "synthesis": {
            "status": consensus_status,
            "summary": consensus_summary,
            "flag_for_review": flag_for_review,
            "architecture_note": (
                "Models operate as independent decoupled estimators. "
                "Probabilities are NOT blended via hardcoded mathematical weighting, "
                "in strict adherence to scientific integrity. A unified fusion model "
                "requires verified spatiotemporally matched incident data."
            )
        }
    }
    return combined_output


def main():
    parser = argparse.ArgumentParser(description="WaterWatch Combined Prediction & Verification Pipeline")
    parser.add_argument("--rainfall_mm", type=float, required=True, help="Current 24-hr rainfall in mm")
    parser.add_argument("--image", type=str, required=True, help="Path to input roadway image")
    parser.add_argument("--location", type=str, default="Nagpur", help="Location or station identifier")
    parser.add_argument("--prev1_mm", type=float, default=0.0, help="Previous day rainfall (lag-1) in mm")
    parser.add_argument("--prev2_mm", type=float, default=0.0, help="2-days prior rainfall (lag-2) in mm")
    parser.add_argument("--api_7day", type=float, default=None, help="7-day Antecedent Precipitation Index")
    parser.add_argument("--conf", type=float, default=0.25, help="Detection confidence threshold")
    parser.add_argument("--save", action="store_true", help="Save annotated detection image")
    parser.add_argument("--output_dir", type=str, default="runs/combined", help="Output directory")
    parser.add_argument("--json", action="store_true", help="Output pure JSON")

    args = parser.parse_args()

    result = run_combined_pipeline(
        rainfall_mm=args.rainfall_mm,
        image_path=args.image,
        location=args.location,
        prev1_mm=args.prev1_mm,
        prev2_mm=args.prev2_mm,
        api_7day=args.api_7day,
        conf_thresh=args.conf,
        save_annotated=args.save,
        output_dir=args.output_dir
    )

    if args.json:
        print(json.dumps(result, indent=2))
    else:
        print("\n" + "=" * 70)
        print("   WATERWATCH AI — COMBINED PREDICTION & VERIFICATION PIPELINE")
        print("=" * 70)
        print(f"  Location              : {result['location']}")
        print(f"  Timestamp             : {result['execution_timestamp']}")
        print("  " + "-" * 68)
        print("  [SIGNAL 1: RAINFALL-BASED RISK ESTIMATION]")
        print(f"    Rainfall Measured   : {result['rainfall_component']['current_rainfall_mm']} mm ({result['rainfall_component']['imd_category']})")
        print(f"    7-Day API           : {result['rainfall_component']['api_7day']} mm")
        print(f"    Hydrological Risk   : {result['rainfall_component']['rainfall_risk_score']:.4f} [{result['rainfall_component']['risk_level'].upper()}]")
        print(f"    Model Engine        : {result['rainfall_component']['model_type']}")
        print("  " + "-" * 68)
        print("  [SIGNAL 2: IMAGE-BASED GROUND VERIFICATION]")
        print(f"    Image Source        : {Path(result['image_component']['image_path']).name}")
        detected_str = "YES (Ponding Observed)" if result['image_component']['waterlogging_detected'] else "NO (Clear Surface)"
        print(f"    Visual Waterlogging : {detected_str}")
        print(f"    Bounding Boxes      : {result['image_component']['detection_count']}")
        if result['image_component']['annotated_image_path']:
            print(f"    Annotated Image     : {result['image_component']['annotated_image_path']}")
        print("  " + "=" * 68)
        print("  [SYNTHESIS & DISAGREEMENT AUDIT]")
        print(f"    Consensus Status    : {result['synthesis']['status']}")
        print(f"    Review Required     : {'YES - FLAG RAISED' if result['synthesis']['flag_for_review'] else 'NO'}")
        print(f"    Operational Note    : {result['synthesis']['summary']}")
        print("=" * 70 + "\n")


if __name__ == "__main__":
    main()
