"""
WaterWatch AI - Waterlogging Event Ingestion & Feature Matching Engine
Defines the schema for ground-truth waterlogging events and links verified incidents
to antecedent meteorological observations using strict spatiotemporal matching rules.
"""

import os
import sys
import json
import math
from pathlib import Path
import pandas as pd
import numpy as np

PROJECT_ROOT = Path(__file__).resolve().parent.parent
DATA_DIR = PROJECT_ROOT / "data"
PROCESSED_DIR = DATA_DIR / "processed"
MANIFESTS_DIR = DATA_DIR / "manifests"
REPORTS_DIR = PROJECT_ROOT / "reports"

MANIFESTS_DIR.mkdir(parents=True, exist_ok=True)
REPORTS_DIR.mkdir(parents=True, exist_ok=True)


EVENT_SCHEMA = {
    "$schema": "http://json-schema.org/draft-07/schema#",
    "title": "WaterWatchAI_WaterloggingEvent",
    "type": "object",
    "required": [
        "event_id",
        "timestamp_start",
        "latitude",
        "longitude",
        "district",
        "waterlogged_label",
        "verification_status"
    ],
    "properties": {
        "event_id": {
            "type": "string",
            "description": "Unique event identifier (e.g., WW-NGP-2024-001)"
        },
        "timestamp_start": {
            "type": "string",
            "format": "date-time",
            "description": "ISO 8601 timestamp of incident onset (e.g., 2024-07-21T14:30:00+05:30)"
        },
        "timestamp_end": {
            "type": ["string", "null"],
            "format": "date-time",
            "description": "ISO 8601 timestamp when water completely receded"
        },
        "latitude": {
            "type": "number",
            "minimum": 15.0,
            "maximum": 23.0,
            "description": "WGS-84 Latitude within Maharashtra"
        },
        "longitude": {
            "type": "number",
            "minimum": 72.0,
            "maximum": 82.0,
            "description": "WGS-84 Longitude within Maharashtra"
        },
        "location_name": {
            "type": "string",
            "description": "Specific landmark or junction (e.g., Sitabuldi Flyover, Nagpur)"
        },
        "district": {
            "type": "string",
            "description": "District name (e.g., Nagpur, Pune, Mumbai)"
        },
        "waterlogged_label": {
            "type": "integer",
            "enum": [0, 1],
            "description": "1 = Waterlogging occurred, 0 = Verified non-waterlogged control"
        },
        "severity_level": {
            "type": "string",
            "enum": ["None", "Low", "Moderate", "Severe", "Critical"],
            "description": "Severity of disruption"
        },
        "water_depth_cm": {
            "type": ["number", "null"],
            "description": "Measured or estimated flood water depth in centimeters"
        },
        "source_type": {
            "type": "string",
            "enum": [
                "Municipal Control Room",
                "Traffic Police Log",
                "Citizen Disaster App",
                "Verified Media Report",
                "Field Inspection"
            ],
            "description": "Source authority"
        },
        "verification_status": {
            "type": "string",
            "enum": ["Verified_Official", "Verified_Field", "Unverified"],
            "description": "Verification level"
        }
    }
}


def haversine_distance_km(lat1, lon1, lat2, lon2):
    """Computes great-circle distance between two GPS coordinates in kilometers."""
    R = 6371.0
    phi1 = math.radians(lat1)
    phi2 = math.radians(lat2)
    delta_phi = math.radians(lat2 - lat1)
    delta_lambda = math.radians(lon2 - lon1)

    a = (math.sin(delta_phi / 2.0) ** 2 +
         math.cos(phi1) * math.cos(phi2) * math.sin(delta_lambda / 2.0) ** 2)
    c = 2.0 * math.atan2(math.sqrt(a), math.sqrt(1.0 - a))
    return R * c


def generate_event_schema_and_template():
    """Writes the JSON schema and a CSV template for collecting future verified events."""
    schema_path = MANIFESTS_DIR / "waterlogging_event_schema.json"
    with open(schema_path, "w", encoding="utf-8") as f:
        json.dump(EVENT_SCHEMA, f, indent=2)
    print(f"Generated event JSON schema: {schema_path}")

    # Generate CSV template
    template_cols = [
        "event_id", "timestamp_start", "timestamp_end", "latitude", "longitude",
        "location_name", "district", "waterlogged_label", "severity_level",
        "water_depth_cm", "source_type", "verification_status"
    ]
    template_df = pd.DataFrame(columns=template_cols)
    template_path = MANIFESTS_DIR / "waterlogging_event_template.csv"
    template_df.to_csv(template_path, index=False)
    print(f"Generated event collection template: {template_path}")


def match_events_to_rainfall(events_csv_path, max_station_dist_km=25.0):
    """
    Matches verified waterlogging events to preceding rainfall conditions.
    Requires an actual verified events CSV.
    """
    if not os.path.exists(events_csv_path):
        print(f"Event file {events_csv_path} does not exist.")
        return None

    events_df = pd.read_csv(events_csv_path)
    if events_df.empty:
        print("Event file is empty.")
        return None

    daily_path = PROCESSED_DIR / "rainfall_daily_features.csv"
    if not daily_path.exists():
        raise FileNotFoundError("Missing processed rainfall daily features.")

    daily_df = pd.read_csv(daily_path)
    daily_df["date"] = pd.to_datetime(daily_df["date"])

    matched_records = []
    print(f"Matching {len(events_df)} candidate events against station network...")

    stations = daily_df[["station_name", "district_name", "latitude", "longitude"]].drop_duplicates().to_dict("records")

    for _, event in events_df.iterrows():
        e_lat = event["latitude"]
        e_lon = event["longitude"]
        e_time = pd.to_datetime(event["timestamp_start"])
        e_date = e_time.date()

        # Find closest station
        closest_st = None
        min_dist = float("inf")
        for st in stations:
            if pd.notna(st["latitude"]) and pd.notna(st["longitude"]):
                d = haversine_distance_km(e_lat, e_lon, st["latitude"], st["longitude"])
                if d < min_dist:
                    min_dist = d
                    closest_st = st

        if closest_st and min_dist <= max_station_dist_km:
            st_name = closest_st["station_name"]
            st_data = daily_df[(daily_df["station_name"] == st_name) & (daily_df["date"].dt.date == e_date)]
            if not st_data.empty:
                r_row = st_data.iloc[0].to_dict()
                r_row.update(event.to_dict())
                r_row["station_distance_km"] = round(min_dist, 2)
                matched_records.append(r_row)

    if not matched_records:
        print("No events matched within criteria.")
        return None

    matched_df = pd.DataFrame(matched_records)
    out_path = PROCESSED_DIR / "matched_waterlogging_dataset.csv"
    matched_df.to_csv(out_path, index=False)
    print(f"Successfully generated matched dataset with {len(matched_df)} instances: {out_path}")
    return matched_df


def audit_available_events():
    """
    Checks if any verified events file currently exists in raw, dataset, or manifest dirs.
    Documents the outcome honestly.
    """
    print("=" * 60)
    print("AUDITING WATERLOGGING OUTCOME LABELS")
    print("=" * 60)

    generate_event_schema_and_template()

    # Look for candidate event CSVs
    candidate_files = list(DATA_DIR.rglob("*event*.csv")) + list(PROJECT_ROOT.glob("*event*.csv"))
    # Exclude templates and quality reports
    candidate_files = [f for f in candidate_files if "template" not in f.name and "schema" not in f.name and "quality" not in f.name]

    if not candidate_files:
        status_report = (
            "STATUS: NO GROUND-TRUTH WATERLOGGING OUTCOME LABELS AVAILABLE IN WORKSPACE\n"
            "-------------------------------------------------------------------------\n"
            "1. Meteorological datasets contain physical precipitation measurements (mm) but no\n"
            "   flood/waterlogging incident logs, traffic police advisories, or municipal tickets.\n"
            "2. Roboflow and Kaggle image archives contain road scenes and visual bounding boxes/masks\n"
            "   without capture timestamps, GPS coordinates, or linkage to Maharashtra rain stations.\n"
            "3. SCIENTIFIC INTEGRITY MANDATE: We do not invent synthetic labels or pretend that a\n"
            "   rainfall threshold equals waterlogging ground truth.\n"
            "4. A formal ingestion schema has been saved at:\n"
            f"   {MANIFESTS_DIR / 'waterlogging_event_schema.json'}\n"
            "5. When verified municipal municipal waterlogging logs are provided, execute:\n"
            "   python scripts/build_event_dataset.py --events <path_to_events.csv>\n"
        )
        print(status_report)
        status_path = REPORTS_DIR / "supervised_linkage_audit.txt"
        with open(status_path, "w", encoding="utf-8") as f:
            f.write(status_report)
        return False
    else:
        print(f"Found candidate event file: {candidate_files[0]}")
        match_events_to_rainfall(candidate_files[0])
        return True


def main():
    import argparse
    parser = argparse.ArgumentParser(description="WaterWatch Event Dataset Builder")
    parser.add_argument("--events", type=str, default=None, help="Path to verified event records CSV")
    parser.add_argument("--max_dist_km", type=float, default=25.0, help="Max distance to weather station")
    args = parser.parse_args()

    if args.events:
        match_events_to_rainfall(args.events, args.max_dist_km)
    else:
        audit_available_events()


if __name__ == "__main__":
    main()
