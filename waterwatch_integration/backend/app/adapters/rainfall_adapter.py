"""
WaterWatch AI Integration - Read-Only Rainfall Model Adapter
Integrates with models/rainfall/synthetic_rainfall_model.joblib without modifying existing files.
"""

from typing import Dict, Any, List
import pandas as pd
import numpy as np
import joblib
from waterwatch_integration.backend.app.config import RAINFALL_MODEL_PATH, METEOROLOGICAL_BASELINE_PATH

EXPECTED_FEATURES = [
    "rainfall_1h_mm",
    "rainfall_3h_mm",
    "rainfall_6h_mm",
    "rainfall_24h_mm",
    "rainfall_prev_72h_mm",
    "drainage_capacity_proxy"
]

RISK_THRESHOLDS = {
    "LOW": 0.35,
    "MODERATE": 0.65
}


class RainfallModelAdapter:
    """Read-only adapter for the trained experimental rainfall model."""

    def __init__(self):
        self._model = None
        self._model_path = None
        self._load_model()

    def _load_model(self):
        if RAINFALL_MODEL_PATH.exists():
            try:
                self._model = joblib.load(RAINFALL_MODEL_PATH)
                self._model_path = RAINFALL_MODEL_PATH
            except Exception as e:
                self._model = None
                self._load_error = str(e)
        else:
            self._model = None
            self._load_error = f"Model artifact not found at {RAINFALL_MODEL_PATH}"

    def is_available(self) -> bool:
        return self._model is not None

    def get_status(self) -> Dict[str, Any]:
        return {
            "model_type": "LogisticRegression (StandardScaler pipeline)" if self.is_available() else "Unavailable",
            "artifact_path": str(self._model_path) if self._model_path else str(RAINFALL_MODEL_PATH),
            "is_available": self.is_available(),
            "training_data_status": "SYNTHETIC_EXPERIMENTAL",
            "feature_schema": EXPECTED_FEATURES,
            "readiness": "READY (Experimental Synthetic Integration)",
            "limitations": "Trained on synthetic demonstration data. Not calibrated for official municipal emergency response."
        }

    def predict(self, features: Dict[str, float], locality: str = "Nagpur") -> Dict[str, Any]:
        """
        Runs read-only inference against the serialized experimental pipeline.
        """
        if not self.is_available():
            raise RuntimeError(f"Rainfall model is not available: {getattr(self, '_load_error', 'Not loaded')}")

        # Validate feature completeness
        missing = [f for f in EXPECTED_FEATURES if f not in features]
        if missing:
            raise ValueError(f"Missing required rainfall features: {missing}")

        warnings = []
        for k in EXPECTED_FEATURES:
            val = float(features[k])
            if np.isnan(val) or np.isinf(val):
                raise ValueError(f"Feature '{k}' cannot be NaN or Inf")
            if val < 0.0:
                raise ValueError(f"Feature '{k}' cannot be negative: {val}")

        # Check rainfall window accumulation monotonicity
        r1, r3, r6, r24 = features["rainfall_1h_mm"], features["rainfall_3h_mm"], features["rainfall_6h_mm"], features["rainfall_24h_mm"]
        if r1 > r3 or r3 > r6 or r6 > r24:
            warnings.append(f"Cumulative window monotonicity anomaly: 1h({r1}) <= 3h({r3}) <= 6h({r6}) <= 24h({r24})")

        # Assemble DataFrame with strict feature order
        df_X = pd.DataFrame([{f: float(features[f]) for f in EXPECTED_FEATURES}])[EXPECTED_FEATURES]

        pred_class = int(self._model.predict(df_X)[0])
        if hasattr(self._model, "predict_proba"):
            probs = self._model.predict_proba(df_X)[0]
            probability = round(float(probs[1]), 4)
        else:
            probability = float(pred_class)

        if probability < RISK_THRESHOLDS["LOW"]:
            risk_category = "LOW"
        elif probability < RISK_THRESHOLDS["MODERATE"]:
            risk_category = "MODERATE"
        else:
            risk_category = "HIGH"

        return {
            "location": locality,
            "predicted_class": pred_class,
            "waterlogging_predicted": bool(pred_class == 1),
            "predicted_probability": probability,
            "risk_category": risk_category,
            "model_name": type(self._model.named_steps.get("clf", self._model)).__name__,
            "model_version": "1.0.0-synthetic",
            "training_data_status": "SYNTHETIC_EXPERIMENTAL",
            "validation_warnings": warnings,
            "input_features": {f: float(features[f]) for f in EXPECTED_FEATURES},
            "scientific_disclaimer": (
                "EXPERIMENTAL MODEL INFERENCE: Trained on synthetic demonstration data. "
                "The probability score reflects synthetic activation, NOT calibrated real-world flood depth or municipal guarantees."
            )
        }


# Singleton instance
rainfall_adapter = RainfallModelAdapter()
