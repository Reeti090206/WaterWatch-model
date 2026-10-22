"""
WaterWatch AI - Waterlogging Event Dataset Validation & Linkage Auditor
Validates event CSV records against waterlogging_event_schema.json,
checks timestamp & coordinate validity, and audits spatiotemporal matchability
against the active rainfall station observation network.
"""

import os
import sys
import math
import json
import argparse
from pathlib import Path
from datetime import datetime
import pandas as pd

PROJECT_ROOT = Path(__file__).resolve().parent.parent
MANIFESTS_DIR = PROJECT_ROOT / "data" / "manifests"
PROCESSED_DIR = PROJECT_ROOT / "data" / "processed"
REPORTS_DIR = PROJECT_ROOT / "reports"
SCHEMA_PATH = MANIFESTS_DIR / "waterlogging_event_schema.json"

REQUIRED_FIELDS = [
    "event_id",
    "location_id",
    "latitude",
    "longitude",
    "event_start_time",
    "waterlogging_observed",
    "evidence_type",
    "evidence_source",
    "verification_status",
    "annotator_id"
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


def haversine_km(lat1, lon1, lat2, lon2):
    R = 6371.0
    phi1, phi2 = math.radians(lat1), math.radians(lat2)
    dphi = math.radians(lat2 - lat1)
    dlam = math.radians(lon2 - lon1)
    a = math.sin(dphi / 2.0) ** 2 + math.cos(phi1) * math.cos(phi2) * math.sin(dlam / 2.0) ** 2
    return 2.0 * R * math.atan2(math.sqrt(a), math.sqrt(1.0 - a))


def validate_events_file(file_path, max_distance_km=25.0):
    print("=" * 65)
    print("WATERWATCH AI — EVENT VALIDATION & RAINFALL LINKAGE AUDIT")
    print("=" * 65)

    path = Path(file_path)
    if not path.exists():
        raise FileNotFoundError(f"Event file not found: {path}")

    df = pd.read_csv(path)
    print(f"Loaded {len(df)} records from {path.name}")

    # Backward compatibility column mapping if old template names were used
    col_aliases = {
        "timestamp_start": "event_start_time",
        "timestamp_end": "event_end_time",
        "waterlogged_label": "waterlogging_observed",
        "source_type": "evidence_type",
        "location_name": "location_id"
    }
    df = df.rename(columns=col_aliases)

    # 1. Structural Schema Validation
    record_audits = []
    total_valid = 0
    total_invalid = 0

    for idx, row in df.iterrows():
        errors = []
        warnings = []
        rec_id = row.get("event_id", f"row_{idx}")

        # Check required fields
        for rf in REQUIRED_FIELDS:
            if rf not in row or pd.isna(row[rf]) or str(row[rf]).strip() == "":
                errors.append(f"Missing required field: '{rf}'")

        # Outcome check
        obs = row.get("waterlogging_observed")
        if pd.notna(obs):
            try:
                obs_int = int(obs)
                if obs_int not in [0, 1]:
                    errors.append(f"Invalid waterlogging_observed: {obs} (must be 0 or 1)")
            except (ValueError, TypeError):
                errors.append(f"Invalid waterlogging_observed: {obs} (must be integer 0 or 1)")

        # Coordinates check
        lat = row.get("latitude")
        lon = row.get("longitude")
        valid_coords = False
        if pd.notna(lat) and pd.notna(lon):
            try:
                lat_f, lon_f = float(lat), float(lon)
                if not (15.0 <= lat_f <= 23.5):
                    warnings.append(f"Latitude {lat_f:.4f} outside Maharashtra reference range (15.0-23.5)")
                if not (72.0 <= lon_f <= 82.5):
                    warnings.append(f"Longitude {lon_f:.4f} outside Maharashtra reference range (72.0-82.5)")
                valid_coords = True
            except ValueError:
                errors.append(f"Coordinates non-numeric: lat={lat}, lon={lon}")
        else:
            errors.append("Latitude or Longitude is null")

        # Timestamp check
        t_start = row.get("event_start_time")
        start_dt = None
        if pd.notna(t_start):
            try:
                start_dt = pd.to_datetime(t_start)
            except Exception:
                errors.append(f"Unparseable event_start_time: '{t_start}'")
        else:
            errors.append("event_start_time is null")

        # Enum check
        ev_type = row.get("evidence_type")
        if pd.notna(ev_type) and ev_type not in ALLOWED_EVIDENCE:
            warnings.append(f"Non-standard evidence_type: '{ev_type}'")

        v_status = row.get("verification_status")
        if pd.notna(v_status) and v_status not in ALLOWED_STATUS:
            warnings.append(f"Non-standard verification_status: '{v_status}'")

        is_valid = len(errors) == 0
        if is_valid:
            total_valid += 1
        else:
            total_invalid += 1

        record_audits.append({
            "event_id": rec_id,
            "is_schema_valid": is_valid,
            "errors": errors,
            "warnings": warnings,
            "lat": float(lat) if valid_coords else None,
            "lon": float(lon) if valid_coords else None,
            "start_dt": start_dt,
            "raw_row": row.to_dict()
        })

    # 2. Spatiotemporal Rainfall Matching Audit
    daily_feat_path = PROCESSED_DIR / "rainfall_daily_features.csv"
    catalog_path = REPORTS_DIR / "station_catalog.csv"

    matched_count = 0
    unmatched_distance_count = 0
    unmatched_temporal_count = 0

    if daily_feat_path.exists():
        daily_df = pd.read_csv(daily_feat_path)
        daily_df["date"] = pd.to_datetime(daily_df["date"]).dt.date
        stations = daily_df[["station_name", "district_name", "latitude", "longitude"]].drop_duplicates().dropna(subset=["latitude", "longitude"]).to_dict("records")
    else:
        stations = []

    for audit in record_audits:
        if not audit["is_schema_valid"] or audit["lat"] is None or audit["start_dt"] is None:
            audit["match_status"] = "Incomplete_Record"
            continue

        if not stations:
            audit["match_status"] = "No_Rainfall_Stations_Available"
            continue

        e_lat, e_lon = audit["lat"], audit["lon"]
        e_date = audit["start_dt"].date()

        # Find closest station
        closest_st = None
        min_dist = float("inf")
        for st in stations:
            d = haversine_km(e_lat, e_lon, st["latitude"], st["longitude"])
            if d < min_dist:
                min_dist = d
                closest_st = st

        audit["closest_station"] = closest_st["station_name"] if closest_st else None
        audit["station_distance_km"] = round(min_dist, 2) if closest_st else None

        if min_dist > max_distance_km:
            audit["match_status"] = f"Unmatched_Too_Far ({min_dist:.1f} km > {max_distance_km} km)"
            unmatched_distance_count += 1
        else:
            # Check temporal presence
            st_name = closest_st["station_name"]
            has_reading = not daily_df[(daily_df["station_name"] == st_name) & (daily_df["date"] == e_date)].empty
            if has_reading:
                audit["match_status"] = "MATCHED"
                matched_count += 1
            else:
                audit["match_status"] = f"Unmatched_Date_Missing ({e_date} not in station records)"
                unmatched_temporal_count += 1

    # Print summary
    print("\n--- Validation & Linkage Summary ---")
    print(f"Total Records Evaluated : {len(df)}")
    print(f"Schema Valid Records    : {total_valid} ({total_valid / len(df) * 100:.1f}%)")
    print(f"Schema Invalid Records  : {total_invalid}")
    print(f"Matched to Rain Station : {matched_count}")
    print(f"Unmatched (Too distant) : {unmatched_distance_count}")
    print(f"Unmatched (Date absent) : {unmatched_temporal_count}")

    # Generate Markdown Report
    md = [
        "# WaterWatch AI — Waterlogging Event Validation & Linkage Audit Report\n",
        f"**File Evaluated**: `{path.name}`",
        f"**Audit Timestamp**: `{datetime.now().isoformat()}`",
        f"**Matching Distance Threshold**: `{max_distance_km} km`\n",
        "## 1. Quality Summary",
        f"- **Total Rows Audited**: {len(df)}",
        f"- **Schema Conforming**: {total_valid} ({total_valid / len(df) * 100:.1f}%)",
        f"- **Schema Violations**: {total_invalid}",
        f"- **Successfully Linked to Antecedent Rainfall**: {matched_count}",
        f"- **Unmatched due to Spatial Distance (> {max_distance_km} km)**: {unmatched_distance_count}",
        f"- **Unmatched due to Temporal Absence in Rainfall Records**: {unmatched_temporal_count}\n",
        "## 2. Detailed Record Audit\n",
        "| Event ID | Schema Status | Linkage Status | Closest Station | Distance (km) | Issues / Notes |",
        "|---|---|---|---|---|---|"
    ]

    for a in record_audits:
        issues = "; ".join(a["errors"] + a["warnings"]) if (a["errors"] or a["warnings"]) else "None"
        st_name = a.get("closest_station", "N/A")
        dist = f"{a.get('station_distance_km', 'N/A')}"
        status_str = "VALID" if a["is_schema_valid"] else "INVALID"
        md.append(f"| {a['event_id']} | {status_str} | {a.get('match_status', 'N/A')} | {st_name} | {dist} | {issues} |")

    report_path = REPORTS_DIR / "event_validation_and_linkage_report.md"
    with open(report_path, "w", encoding="utf-8") as f:
        f.write("\n".join(md) + "\n")
    print(f"\nSaved detailed audit report to {report_path}")

    return {
        "total": len(df),
        "valid": total_valid,
        "invalid": total_invalid,
        "matched": matched_count,
        "unmatched_distance": unmatched_distance_count,
        "unmatched_temporal": unmatched_temporal_count
    }


def main():
    parser = argparse.ArgumentParser(description="WaterWatch Event Validation & Linkage Auditor")
    parser.add_argument("--events", type=str, default=str(MANIFESTS_DIR / "waterlogging_event_template.csv"), help="Path to events CSV file")
    parser.add_argument("--max_dist_km", type=float, default=25.0, help="Max distance threshold to weather station (km)")
    args = parser.parse_args()

    validate_events_file(args.events, args.max_dist_km)


if __name__ == "__main__":
    main()
