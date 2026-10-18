"""
WaterWatch AI - Rainfall Model Utilities & Baseline Estimator
Provides the reusable baseline estimator and feature definitions.
"""

import numpy as np
import pandas as pd

FEATURE_COLUMNS = [
    "rainfall_mm",
    "rainfall_prev1_day_mm",
    "rainfall_prev2_day_mm",
    "rainfall_2day_total_mm",
    "rainfall_3day_total_mm",
    "api_7day",
    "rainfall_trend_ratio",
    "is_monsoon"
]


class ExperimentalMeteorologicalRiskBaseline:
    """
    Transparent rule-based meteorological risk scorer based on IMD rainfall intensity
    and 7-day Antecedent Precipitation Index (API).
    IMPORTANT: This is NOT a validated predictive ML model; it serves as an empirical
    hydrological reference until ground-truth event labels are collected.
    """
    def __init__(self):
        self.name = "ExperimentalMeteorologicalRiskBaseline"
        self.assumptions = [
            "No ground-truth municipal waterlogging events are currently matched.",
            "Rainfall > 64.5 mm/day (IMD Heavy) creates elevated surface runoff potential.",
            "Antecedent 7-day API > 80 mm reflects high soil moisture saturation.",
            "Risk scores represent meteorological hazard, not urban drainage capacity."
        ]

    def predict_risk(self, X_df):
        scores = []
        for _, row in X_df.iterrows():
            r = row.get("rainfall_mm", 0.0)
            api = row.get("api_7day", 0.0)
            if pd.isna(r):
                scores.append(0.0)
                continue

            # Acute single-day component [0.0 - 0.60]
            if r <= 15.5:
                acute = (r / 15.5) * 0.10
            elif r <= 64.4:
                acute = 0.10 + ((r - 15.5) / (64.4 - 15.5)) * 0.25
            elif r <= 115.5:
                acute = 0.35 + ((r - 64.4) / (115.5 - 64.4)) * 0.15
            elif r <= 204.4:
                acute = 0.50 + ((r - 115.5) / (204.4 - 115.5)) * 0.10
            else:
                acute = 0.60

            # Antecedent saturation component [0.0 - 0.40]
            ant = min(0.40, (api / 120.0) * 0.40)
            scores.append(round(float(min(1.0, acute + ant)), 4))
        return np.array(scores)

    def predict_proba(self, X_df):
        risks = self.predict_risk(X_df)
        return np.vstack([1.0 - risks, risks]).T

    def predict(self, X_df, threshold=0.45):
        risks = self.predict_risk(X_df)
        return (risks >= threshold).astype(int)
