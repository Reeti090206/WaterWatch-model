"""
Unit and Integration Tests for WaterWatch AI Rainfall Processing Pipeline
Tests timestamp parsing, deduplication, interval preservation, and station geographic coverage.
"""

import os
from pathlib import Path
import pandas as pd
import numpy as np
import pytest

PROJECT_ROOT = Path(__file__).resolve().parent.parent
PROCESSED_DIR = PROJECT_ROOT / "data" / "processed"
REPORTS_DIR = PROJECT_ROOT / "reports"


def test_processed_rainfall_files_exist():
    daily_file = PROCESSED_DIR / "rainfall_daily_observed.csv"
    hourly_file = PROCESSED_DIR / "rainfall_hourly_observed.csv"
    catalog_file = REPORTS_DIR / "station_catalog.csv"

    assert daily_file.exists(), f"Missing {daily_file}"
    assert hourly_file.exists(), f"Missing {hourly_file}"
    assert catalog_file.exists(), f"Missing {catalog_file}"


def test_daily_rainfall_integrity():
    daily_file = PROCESSED_DIR / "rainfall_daily_observed.csv"
    df = pd.read_csv(daily_file)

    assert len(df) > 50000, f"Expected >50,000 daily records, found {len(df)}"
    assert "station_name" in df.columns
    assert "rainfall_mm" in df.columns
    assert "timestamp_ist" in df.columns
    assert "is_nagpur" in df.columns

    # Check zero unparseable timestamps
    assert df["timestamp_ist"].isna().sum() == 0, "Found null timestamps in daily observed data"

    # Check non-negative rainfall
    assert (df["rainfall_mm"] < 0).sum() == 0, "Found negative rainfall in daily data"

    # Check deduplication
    dups = df.duplicated(subset=["station_name", "date"]).sum()
    assert dups == 0, f"Found {dups} duplicate station-date pairs in daily observed data"


def test_hourly_null_preservation():
    """Verify that unrecorded telemetry intervals are NOT falsely imputed as zero rainfall."""
    hourly_file = PROCESSED_DIR / "rainfall_hourly_observed.csv"
    df = pd.read_csv(hourly_file)

    assert "is_measured" in df.columns
    unmeasured = (~df["is_measured"]).sum()
    assert unmeasured > 0, "Telemetry nulls were improperly dropped or overwritten"

    # Ensure rainfall_mm is NaN when is_measured is False
    assert df[~df["is_measured"]]["rainfall_mm"].isna().all(), "Unmeasured rows must be NaN, not zero"


def test_station_catalog_and_nagpur_coverage():
    """Verify that station catalog contains valid coordinates and Nagpur coverage."""
    catalog_file = REPORTS_DIR / "station_catalog.csv"
    cat = pd.read_csv(catalog_file)

    assert len(cat) > 100, f"Expected >100 catalogued stations, found {len(cat)}"
    nagpur_stations = cat[cat["is_nagpur"] == True]
    assert len(nagpur_stations) >= 9, f"Expected at least 9 Nagpur stations, found {len(nagpur_stations)}"

    # Check valid Maharashtra latitude and longitude ranges
    valid_lats = cat["latitude"].between(15.0, 23.0)
    valid_lons = cat["longitude"].between(72.0, 82.0)
    assert (valid_lats & valid_lons).sum() / len(cat) > 0.95, "Significant portion of stations outside Maharashtra bounds"
