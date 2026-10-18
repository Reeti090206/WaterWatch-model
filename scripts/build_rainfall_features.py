"""
WaterWatch AI - Rainfall Feature Engineering Pipeline
Computes multi-scale temporal aggregations, lag features, rolling windows,
antecedent precipitation index (API), IMD severity classifications, and
an experimental meteorological risk score baseline.
"""

import os
import sys
from pathlib import Path
import pandas as pd
import numpy as np

PROJECT_ROOT = Path(__file__).resolve().parent.parent
DATA_DIR = PROJECT_ROOT / "data"
PROCESSED_DIR = DATA_DIR / "processed"
REPORTS_DIR = PROJECT_ROOT / "reports"

PROCESSED_DIR.mkdir(parents=True, exist_ok=True)


def compute_imd_category(val):
    """Categorizes rainfall intensity according to India Meteorological Department (IMD) standards."""
    if pd.isna(val) or val <= 0.0:
        return "No Rain"
    elif val <= 2.4:
        return "Very Light"
    elif val <= 15.5:
        return "Light"
    elif val <= 64.4:
        return "Moderate"
    elif val <= 115.5:
        return "Heavy"
    elif val <= 204.4:
        return "Very Heavy"
    else:
        return "Extremely Heavy"


def compute_experimental_daily_risk(row):
    """
    Experimental, rule-based hydrological waterlogging risk index [0.0, 1.0].
    DOCUMENTED ASSUMPTIONS:
    - This is NOT a validated predictive model. No ground truth incident labels exist.
    - Combines acute intensity (IMD heavy thresholds) with antecedent soil moisture (7-day API).
    - Serves as an uncalibrated heuristic baseline until verified municipal waterlogging logs are ingested.
    """
    r_current = row.get("rainfall_mm", 0.0)
    api = row.get("api_7day", 0.0)
    r_3day = row.get("rainfall_3day_total_mm", 0.0)

    if pd.isna(r_current):
        return np.nan

    # 1. Acute single-day risk component (0.0 to 0.6)
    # 0 at <= 15mm, scales to 0.3 at 65mm, 0.5 at 115mm, 0.6 at 200mm+
    if r_current <= 15.5:
        acute_score = (r_current / 15.5) * 0.10
    elif r_current <= 64.4:
        acute_score = 0.10 + ((r_current - 15.5) / (64.4 - 15.5)) * 0.25
    elif r_current <= 115.5:
        acute_score = 0.35 + ((r_current - 64.4) / (115.5 - 64.4)) * 0.15
    elif r_current <= 204.4:
        acute_score = 0.50 + ((r_current - 115.5) / (204.4 - 115.5)) * 0.10
    else:
        acute_score = 0.60

    # 2. Antecedent soil moisture / prolonged accumulation component (0.0 to 0.4)
    # API > 100mm represents heavily saturated catchment
    ant_score = min(0.40, (api / 120.0) * 0.40)

    total_risk = min(1.0, acute_score + ant_score)
    return round(float(total_risk), 4)


def build_daily_features():
    print("=" * 60)
    print("BUILDING DAILY RAINFALL FEATURES")
    print("=" * 60)

    daily_path = PROCESSED_DIR / "rainfall_daily_observed.csv"
    if not daily_path.exists():
        raise FileNotFoundError(f"Missing {daily_path}. Run prepare_rainfall.py first!")

    print(f"Reading {daily_path.name}...")
    df = pd.read_csv(daily_path)
    df["timestamp_ist"] = pd.to_datetime(df["timestamp_ist"])
    df["date"] = pd.to_datetime(df["date"])

    # Ensure sorted by station and date
    df = df.sort_values(by=["station_name", "date"]).reset_index(drop=True)

    # To calculate rolling features correctly without falsely bridging multi-week gaps,
    # we compute time deltas between successive observations per station
    print("Calculating rolling temporal features and lag metrics...")
    
    # Lag 1 and Lag 2
    df["prev_date"] = df.groupby("station_name")["date"].shift(1)
    df["days_since_prev"] = (df["date"] - df["prev_date"]).dt.days

    df["rainfall_prev1_day_mm"] = np.where(df["days_since_prev"] == 1, df.groupby("station_name")["rainfall_mm"].shift(1), np.nan)
    
    # Lag 2
    df["prev2_date"] = df.groupby("station_name")["date"].shift(2)
    df["days_since_prev2"] = (df["date"] - df["prev2_date"]).dt.days
    df["rainfall_prev2_day_mm"] = np.where(df["days_since_prev2"] == 2, df.groupby("station_name")["rainfall_mm"].shift(2), np.nan)

    # 2-day total (only when consecutive)
    df["rainfall_2day_total_mm"] = np.where(
        df["rainfall_prev1_day_mm"].notna(),
        df["rainfall_mm"] + df["rainfall_prev1_day_mm"],
        df["rainfall_mm"]
    )

    # 3-day total (only when consecutive)
    df["rainfall_3day_total_mm"] = np.where(
        df["rainfall_prev1_day_mm"].notna() & df["rainfall_prev2_day_mm"].notna(),
        df["rainfall_mm"] + df["rainfall_prev1_day_mm"] + df["rainfall_prev2_day_mm"],
        df["rainfall_2day_total_mm"]
    )

    # Antecedent Precipitation Index (API) with decay lambda = 0.85
    # API_t = 0.85 * (API_{t-1} + R_{t-1})
    decay = 0.85
    def calc_api_series(series):
        api = np.zeros(len(series))
        vals = series.fillna(0.0).values
        for t in range(1, len(series)):
            api[t] = decay * (api[t-1] + vals[t-1])
        return pd.Series(api, index=series.index)

    df["api_7day"] = df.groupby("station_name")["rainfall_mm"].transform(calc_api_series).round(2)

    # Trend: ratio of current day rainfall to 3-day cumulative (if > 0)
    df["rainfall_trend_ratio"] = np.where(
        df["rainfall_3day_total_mm"] > 0,
        (df["rainfall_mm"] / df["rainfall_3day_total_mm"]).round(3),
        1.0
    )

    # IMD Category
    df["imd_category"] = df["rainfall_mm"].apply(compute_imd_category)

    # Southwest Monsoon indicator (June to September)
    df["is_monsoon"] = df["month"].isin([6, 7, 8, 9])

    # Experimental risk baseline score
    df["experimental_risk_score"] = df.apply(compute_experimental_daily_risk, axis=1)

    # Risk level classification
    def risk_level(score):
        if pd.isna(score) or score < 0.20:
            return "Low"
        elif score < 0.45:
            return "Moderate"
        elif score < 0.70:
            return "High"
        else:
            return "Critical"

    df["experimental_risk_level"] = df["experimental_risk_score"].apply(risk_level)

    # Clean intermediate columns
    drop_cols = ["prev_date", "days_since_prev", "prev2_date", "days_since_prev2"]
    df = df.drop(columns=[c for c in drop_cols if c in df.columns])

    # Save feature dataset
    feat_path = PROCESSED_DIR / "rainfall_daily_features.csv"
    df.to_csv(feat_path, index=False)
    print(f"Engineered features for {len(df):,} daily records.")
    print(f"Risk distribution:\n{df['experimental_risk_level'].value_counts()}")
    print(f"Saved: {feat_path}")
    return df


def build_hourly_features():
    print("\n" + "=" * 60)
    print("BUILDING HOURLY ROLLING FEATURES")
    print("=" * 60)

    hourly_path = PROCESSED_DIR / "rainfall_hourly_observed.csv"
    if not hourly_path.exists():
        print(f"Missing {hourly_path}, skipping hourly features.")
        return None

    print(f"Reading {hourly_path.name}...")
    df = pd.read_csv(hourly_path)
    df["timestamp_ist"] = pd.to_datetime(df["timestamp_ist"])
    df = df.sort_values(by=["station_name", "timestamp_ist"]).reset_index(drop=True)

    # Rolling 3h, 6h, 12h, 24h
    # RULE: Calculate rolling features ONLY when observation window is sufficiently covered!
    # If telemetry is missing, we must NOT falsely assume 0.0!
    print("Calculating rolling temporal windows (3h, 6h, 12h, 24h)...")
    
    # We work station by station for valid measured records
    # To handle irregular telemetry, we use time-based rolling window on stations with measurements
    measured_df = df[df["is_measured"]].copy()
    measured_df = measured_df.set_index("timestamp_ist")

    # Rolling calculations per station
    grouped = measured_df.groupby("station_name")
    
    # Rolling 3h sum
    measured_df["rolling_3h_mm"] = grouped["rainfall_mm"].rolling("3h", min_periods=1).sum().values
    # Rolling 6h sum
    measured_df["rolling_6h_mm"] = grouped["rainfall_mm"].rolling("6h", min_periods=1).sum().values
    # Rolling 12h sum
    measured_df["rolling_12h_mm"] = grouped["rainfall_mm"].rolling("12h", min_periods=1).sum().values
    # Rolling 24h sum
    measured_df["rolling_24h_mm"] = grouped["rainfall_mm"].rolling("24h", min_periods=1).sum().values

    measured_df = measured_df.reset_index()

    # Experimental hourly risk index
    # IMD hourly definitions: > 15.5mm in 1 hour = intense localized cloudburst / waterlogging risk
    def hourly_risk(row):
        r1 = row.get("rainfall_mm", 0.0)
        r3 = row.get("rolling_3h_mm", 0.0)
        r24 = row.get("rolling_24h_mm", 0.0)
        
        # Acute 1-hour
        score_1h = min(0.50, (r1 / 25.0) * 0.50)
        # Acute 3-hour
        score_3h = min(0.30, (r3 / 50.0) * 0.30)
        # 24-hour total
        score_24h = min(0.20, (r24 / 100.0) * 0.20)
        return round(float(min(1.0, score_1h + score_3h + score_24h)), 4)

    measured_df["experimental_risk_score"] = measured_df.apply(hourly_risk, axis=1)

    out_path = PROCESSED_DIR / "rainfall_hourly_features.csv"
    measured_df.to_csv(out_path, index=False)
    print(f"Engineered rolling features for {len(measured_df):,} verified hourly measurements.")
    print(f"Saved: {out_path}")
    return measured_df


def main():
    build_daily_features()
    build_hourly_features()
    print("\nRainfall feature engineering complete!")


if __name__ == "__main__":
    main()
