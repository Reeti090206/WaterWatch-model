"""
WaterWatch AI - Waterlogging Event Data Entry & Annotation CLI
Enables operators to record verified waterlogging events and negative control observations
with immediate validation against waterlogging_event_schema.json.
"""

import os
import sys
import argparse
from pathlib import Path
from datetime import datetime
import pandas as pd

PROJECT_ROOT = Path(__file__).resolve().parent.parent
MANIFESTS_DIR = PROJECT_ROOT / "data" / "manifests"
EVENTS_CSV = MANIFESTS_DIR / "waterlogging_events_log.csv"

COLUMNS = [
    "event_id",
    "location_id",
    "latitude",
    "longitude",
    "event_start_time",
    "event_end_time",
    "waterlogging_observed",
    "severity_level",
    "water_depth_cm",
    "evidence_type",
    "evidence_source",
    "verification_status",
    "image_path",
    "annotator_id",
    "notes"
]

ALLOWED_EVIDENCE = [
    "Municipal_Log",
    "Traffic_Police_Log",
    "Physical_Inspection",
    "CCTV_Feed",
    "Citizen_Report_Verified",
    "Automated_Sensor",
    "Media_Verified",
    "Field_Survey"
]

ALLOWED_STATUS = [
    "Verified_Official",
    "Verified_Field",
    "Unverified",
    "Disputed",
    "Rejected"
]

ALLOWED_SEVERITY = ["None", "Low", "Moderate", "Severe", "Critical", "Unknown"]


def validate_record(record):
    """Validates an event record before appending."""
    errors = []
    
    # Required strings
    for req in ["event_id", "location_id", "event_start_time", "evidence_source", "annotator_id"]:
        if not record.get(req) or str(record[req]).strip() == "":
            errors.append(f"Field '{req}' is mandatory and cannot be empty.")

    # Outcome
    if record.get("waterlogging_observed") not in [0, 1]:
        errors.append("waterlogging_observed must be exactly 0 (verified negative control) or 1 (waterlogged).")

    # Coordinates
    try:
        lat = float(record["latitude"])
        lon = float(record["longitude"])
        if not (15.0 <= lat <= 23.5):
            errors.append(f"Latitude {lat} is outside Maharashtra bounds (15.0 to 23.5).")
        if not (72.0 <= lon <= 82.5):
            errors.append(f"Longitude {lon} is outside Maharashtra bounds (72.0 to 82.5).")
    except (ValueError, TypeError):
        errors.append("Latitude and longitude must be valid floating point numbers.")

    # Timestamp
    try:
        t_start = datetime.fromisoformat(record["event_start_time"])
    except (ValueError, TypeError):
        errors.append("event_start_time must be an ISO 8601 formatted timestamp (e.g. 2024-07-22T14:30:00+05:30).")

    if record.get("event_end_time") and str(record["event_end_time"]).strip():
        try:
            t_end = datetime.fromisoformat(record["event_end_time"])
            if t_end < t_start:
                errors.append("event_end_time cannot be earlier than event_start_time.")
        except (ValueError, TypeError):
            errors.append("event_end_time must be an ISO 8601 formatted timestamp.")

    # Enums
    if record.get("evidence_type") not in ALLOWED_EVIDENCE:
        errors.append(f"evidence_type '{record.get('evidence_type')}' not in allowed set: {ALLOWED_EVIDENCE}")

    if record.get("verification_status") not in ALLOWED_STATUS:
        errors.append(f"verification_status '{record.get('verification_status')}' not in allowed set: {ALLOWED_STATUS}")

    sev = record.get("severity_level", "Unknown")
    if sev not in ALLOWED_SEVERITY:
        errors.append(f"severity_level '{sev}' not in allowed set: {ALLOWED_SEVERITY}")

    if record.get("waterlogging_observed") == 0 and sev not in ["None", "Unknown"]:
        errors.append("When waterlogging_observed=0 (negative control), severity_level should be 'None'.")

    return errors


def add_event(record, target_file=None):
    """Appends a validated record to the events CSV."""
    errors = validate_record(record)
    if errors:
        print("ERROR: Record failed validation:")
        for e in errors:
            print(f"  - {e}")
        return False

    out_file = Path(target_file) if target_file else EVENTS_CSV
    out_file.parent.mkdir(parents=True, exist_ok=True)

    if out_file.exists():
        df = pd.read_csv(out_file)
        if record["event_id"] in df["event_id"].astype(str).values:
            print(f"ERROR: Duplicate event_id '{record['event_id']}' already exists in {out_file.name}.")
            return False
    else:
        df = pd.DataFrame(columns=COLUMNS)

    df_new = pd.concat([df, pd.DataFrame([record])], ignore_index=True)
    df_new.to_csv(out_file, index=False)
    print(f"Successfully recorded event '{record['event_id']}' into {out_file}")
    return True


def main():
    parser = argparse.ArgumentParser(description="WaterWatch Event Annotation & Data Entry CLI")
    parser.add_argument("--event_id", type=str, required=True, help="Unique event ID")
    parser.add_argument("--location_id", type=str, required=True, help="Location ID (e.g. NGP-SITABULDI-01)")
    parser.add_argument("--lat", type=float, required=True, help="Latitude (15.0 to 23.5)")
    parser.add_argument("--lon", type=float, required=True, help="Longitude (72.0 to 82.5)")
    parser.add_argument("--start", type=str, required=True, help="ISO 8601 start timestamp (e.g. 2024-07-22T14:30:00+05:30)")
    parser.add_argument("--end", type=str, default=None, help="ISO 8601 end timestamp")
    parser.add_argument("--observed", type=int, required=True, choices=[0, 1], help="1=waterlogging, 0=verified negative control")
    parser.add_argument("--severity", type=str, default="Unknown", choices=ALLOWED_SEVERITY, help="Severity level")
    parser.add_argument("--depth_cm", type=float, default=None, help="Measured flood water depth in cm")
    parser.add_argument("--evidence", type=str, required=True, choices=ALLOWED_EVIDENCE, help="Evidence type")
    parser.add_argument("--source", type=str, required=True, help="Evidence source authority")
    parser.add_argument("--status", type=str, required=True, choices=ALLOWED_STATUS, help="Verification tier")
    parser.add_argument("--image", type=str, default=None, help="Photographic evidence path")
    parser.add_argument("--annotator", type=str, required=True, help="Annotator/Inspector ID")
    parser.add_argument("--notes", type=str, default="", help="Contextual notes")
    parser.add_argument("--target_csv", type=str, default=None, help="Path to destination events CSV")

    args = parser.parse_args()

    record = {
        "event_id": args.event_id,
        "location_id": args.location_id,
        "latitude": args.lat,
        "longitude": args.lon,
        "event_start_time": args.start,
        "event_end_time": args.end,
        "waterlogging_observed": args.observed,
        "severity_level": args.severity,
        "water_depth_cm": args.depth_cm,
        "evidence_type": args.evidence,
        "evidence_source": args.source,
        "verification_status": args.status,
        "image_path": args.image,
        "annotator_id": args.annotator,
        "notes": args.notes
    }

    success = add_event(record, args.target_csv)
    if not success:
        sys.exit(1)


if __name__ == "__main__":
    main()
