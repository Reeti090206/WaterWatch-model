"""
WaterWatch AI - Rainfall Data Processing Pipeline
Processes daily, hourly, and historical rainfall datasets for Maharashtra,
verifying timestamps, coordinates, observation intervals, and coverage (with focus on Nagpur).
"""

import os
import sys
from pathlib import Path
import pandas as pd
import numpy as np

PROJECT_ROOT = Path(__file__).resolve().parent.parent
DATA_DIR = PROJECT_ROOT / "data"
RAW_DIR = DATA_DIR / "raw"
PROCESSED_DIR = DATA_DIR / "processed"
REPORTS_DIR = PROJECT_ROOT / "reports"

PROCESSED_DIR.mkdir(parents=True, exist_ok=True)
REPORTS_DIR.mkdir(parents=True, exist_ok=True)


def find_file(patterns):
    search_dirs = [PROJECT_ROOT, RAW_DIR, PROJECT_ROOT / "dataset"]
    for pattern in patterns:
        for d in search_dirs:
            matches = list(d.glob(pattern))
            if matches:
                return matches[0]
    return None


def process_daily_rainfall():
    print("=" * 60)
    print("PROCESSING DAILY RAINFALL DATASET (2021-2025)")
    print("=" * 60)

    fpath = find_file(["rainfall_manual_daily*.csv", "*manual_daily*.csv"])
    if not fpath:
        raise FileNotFoundError("Could not find manual daily rainfall dataset!")

    print(f"Reading {fpath.name}...")
    df = pd.read_csv(fpath)
    initial_len = len(df)
    print(f"Loaded {initial_len:,} raw rows.")

    # 1. Standardize columns
    rain_col = "Manual Daily Rainfall (mm)"
    rename_map = {
        "Data Acquisition Time": "raw_timestamp",
        rain_col: "rainfall_mm",
        "Station": "station_name",
        "District": "district_name",
        "Tehsil": "tehsil_name",
        "Block": "block_name",
        "Village": "village_name",
        "River": "river_name",
        "Basin": "basin_name",
        "Latitude": "latitude",
        "Longitude": "longitude",
        "Agency": "agency"
    }
    df = df.rename(columns=rename_map)

    # 2. Parse timestamps (format: 04-06-2021 08:30)
    df["timestamp_ist"] = pd.to_datetime(df["raw_timestamp"], format="%d-%m-%Y %H:%M", errors="coerce")
    invalid_dates = df["timestamp_ist"].isna().sum()
    if invalid_dates > 0:
        print(f"Dropping {invalid_dates} rows with unparseable timestamps.")
        df = df.dropna(subset=["timestamp_ist"])

    # Extract date components
    df["date"] = df["timestamp_ist"].dt.date
    df["year"] = df["timestamp_ist"].dt.year
    df["month"] = df["timestamp_ist"].dt.month
    df["day"] = df["timestamp_ist"].dt.day
    df["hour"] = df["timestamp_ist"].dt.hour
    df["observation_window_hours"] = 24

    # 3. Handle duplicates
    dup_mask = df.duplicated(subset=["station_name", "date"], keep="first")
    dup_count = dup_mask.sum()
    if dup_count > 0:
        print(f"Removing {dup_count:,} duplicate observations for the same station and date.")
        df = df[~dup_mask]

    # 4. Clean coordinates
    # Valid bounds for Maharashtra: Lat ~15.0 to ~23.0, Lon ~72.0 to ~82.0
    valid_coords = (
        (df["latitude"].between(15.0, 23.0)) &
        (df["longitude"].between(72.0, 82.0))
    )
    invalid_coords_count = (~valid_coords).sum()
    if invalid_coords_count > 0:
        print(f"Found {invalid_coords_count} observations with out-of-bounds coordinates (flagged).")
    df["valid_coords"] = valid_coords

    # 5. Nagpur Indicator
    df["is_nagpur"] = (
        df["district_name"].astype(str).str.contains("Nagpur", case=False, na=False) |
        df["station_name"].astype(str).str.contains("Nagpur", case=False, na=False)
    )

    # Sort deterministically
    df = df.sort_values(by=["station_name", "timestamp_ist"]).reset_index(drop=True)

    # Output stats
    nagpur_rows = df["is_nagpur"].sum()
    print(f"Processed daily dataset: {len(df):,} clean rows.")
    print(f"  Stations: {df['station_name'].nunique()} | Districts: {df['district_name'].nunique()}")
    print(f"  Nagpur observations: {nagpur_rows:,} across {df[df['is_nagpur']]['station_name'].nunique()} stations")
    print(f"  Rainfall range: {df['rainfall_mm'].min():.2f} mm to {df['rainfall_mm'].max():.2f} mm (mean: {df['rainfall_mm'].mean():.2f} mm)")

    # Save processed daily dataset
    out_path = PROCESSED_DIR / "rainfall_daily_observed.csv"
    df.to_csv(out_path, index=False)
    print(f"Saved: {out_path}")
    return df


def process_hourly_rainfall():
    print("\n" + "=" * 60)
    print("PROCESSING HOURLY TELEMETRY RAINFALL (CWC 2021-2025 & SW 1991-2020)")
    print("=" * 60)

    cwc_path = find_file(["rainfall_tel_hr_cwc*.csv", "*tel_hr_cwc*.csv"])
    sw_path = find_file(["rainfall_tel_hr_maharashtra-sw*.csv", "*1991_2020*.csv"])

    frames = []

    if cwc_path:
        print(f"Reading CWC telemetry: {cwc_path.name}...")
        df_cwc = pd.read_csv(cwc_path)
        df_cwc["source_dataset"] = "cwc_hourly_2021_2025"
        frames.append(df_cwc)

    if sw_path:
        print(f"Reading SW historical telemetry: {sw_path.name}...")
        df_sw = pd.read_csv(sw_path)
        df_sw["source_dataset"] = "sw_hourly_1991_2020"
        frames.append(df_sw)

    if not frames:
        raise FileNotFoundError("No hourly rainfall datasets found!")

    df = pd.concat(frames, ignore_index=True)
    initial_len = len(df)
    print(f"Combined hourly rows: {initial_len:,}")

    rain_col = "Telemetry Hourly Rainfall (mm)"
    rename_map = {
        "Data Acquisition Time": "raw_timestamp",
        rain_col: "rainfall_mm",
        "Station": "station_name",
        "District": "district_name",
        "Tehsil": "tehsil_name",
        "Block": "block_name",
        "Village": "village_name",
        "River": "river_name",
        "Basin": "basin_name",
        "Latitude": "latitude",
        "Longitude": "longitude",
        "Agency": "agency"
    }
    df = df.rename(columns=rename_map)

    # Parse timestamps
    df["timestamp_ist"] = pd.to_datetime(df["raw_timestamp"], format="%d-%m-%Y %H:%M", errors="coerce")
    df = df.dropna(subset=["timestamp_ist"])

    df["date"] = df["timestamp_ist"].dt.date
    df["year"] = df["timestamp_ist"].dt.year
    df["month"] = df["timestamp_ist"].dt.month
    df["day"] = df["timestamp_ist"].dt.day
    df["hour"] = df["timestamp_ist"].dt.hour
    df["observation_window_hours"] = 1

    # CRITICAL RULE: Preserve valid observations, but do NOT impute NaN as 0!
    # We maintain is_measured flag
    df["is_measured"] = df["rainfall_mm"].notna()

    # Deduplicate exact station + timestamp
    dup_mask = df.duplicated(subset=["station_name", "timestamp_ist"], keep="first")
    if dup_mask.sum() > 0:
        print(f"Removing {dup_mask.sum():,} duplicate hourly timestamp records.")
        df = df[~dup_mask]

    # Nagpur indicator
    df["is_nagpur"] = (
        df["district_name"].astype(str).str.contains("Nagpur", case=False, na=False) |
        df["station_name"].astype(str).str.contains("Nagpur", case=False, na=False)
    )

    df = df.sort_values(by=["station_name", "timestamp_ist"]).reset_index(drop=True)

    measured_df = df[df["is_measured"]]
    print(f"Hourly dataset: {len(df):,} total intervals, {len(measured_df):,} verified measurements.")
    print(f"  Stations: {df['station_name'].nunique()} | Districts: {df['district_name'].nunique()}")
    print(f"  Nagpur hourly measurements: {measured_df['is_nagpur'].sum()} rows")

    out_path = PROCESSED_DIR / "rainfall_hourly_observed.csv"
    df.to_csv(out_path, index=False)
    print(f"Saved: {out_path}")
    return df


def generate_station_catalog(df_daily, df_hourly):
    """Build unified station catalog across all available sources."""
    print("\n" + "=" * 60)
    print("BUILDING UNIFIED STATION CATALOG")
    print("=" * 60)

    daily_cat = df_daily.groupby(["station_name", "district_name", "latitude", "longitude", "agency"]).agg(
        total_records=("date", "count"),
        first_recorded_date=("timestamp_ist", "min"),
        last_recorded_date=("timestamp_ist", "max"),
        max_daily_rainfall_mm=("rainfall_mm", "max"),
        mean_daily_rainfall_mm=("rainfall_mm", "mean"),
        is_nagpur=("is_nagpur", "first")
    ).reset_index()
    daily_cat["dataset_type"] = "Daily Manual"

    hourly_valid = df_hourly[df_hourly["is_measured"]]
    hourly_cat = hourly_valid.groupby(["station_name", "district_name", "latitude", "longitude", "agency"]).agg(
        total_records=("hour", "count"),
        first_recorded_date=("timestamp_ist", "min"),
        last_recorded_date=("timestamp_ist", "max"),
        max_daily_rainfall_mm=("rainfall_mm", "max"),
        mean_daily_rainfall_mm=("rainfall_mm", "mean"),
        is_nagpur=("is_nagpur", "first")
    ).reset_index()
    hourly_cat["dataset_type"] = "Hourly Telemetry"

    catalog = pd.concat([daily_cat, hourly_cat], ignore_index=True)
    catalog = catalog.sort_values(by=["is_nagpur", "district_name", "station_name"], ascending=[False, True, True])

    cat_path = REPORTS_DIR / "station_catalog.csv"
    catalog.to_csv(cat_path, index=False)
    print(f"Saved station catalog ({len(catalog)} entries) to {cat_path}")

    # Summary by district
    dist_summary = catalog.groupby(["district_name", "dataset_type"]).agg(
        station_count=("station_name", "nunique"),
        total_records=("total_records", "sum"),
        max_rainfall_mm=("max_daily_rainfall_mm", "max")
    ).reset_index()
    sum_path = REPORTS_DIR / "station_coverage_summary.csv"
    dist_summary.to_csv(sum_path, index=False)
    print(f"Saved district coverage summary to {sum_path}")


def main():
    df_daily = process_daily_rainfall()
    df_hourly = process_hourly_rainfall()
    generate_station_catalog(df_daily, df_hourly)
    print("\nRainfall data processing complete!")


if __name__ == "__main__":
    main()
