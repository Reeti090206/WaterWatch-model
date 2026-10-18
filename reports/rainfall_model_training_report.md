# WaterWatch AI — Rainfall-to-Waterlogging Model Training Status

## Scientific Assessment & Data Integrity Statement

- **Supervised Model Status**: **NOT TRAINED (HEURISTIC BASELINE DEPLOYED)**
- **Reason**: The provided workspace contains Maharashtra rainfall telemetry and manual daily logs (2021–2025), and image archives from Roboflow and Kaggle. However, **none of the datasets contain verified waterlogging incident logs** (timestamps, geolocations, and ground-truth flooded vs non-flooded verification).
- **Strict Anti-Fabrication Compliance**: Under prompt instructions, we strictly do NOT fabricate synthetic waterlogging outcomes, do NOT assume rainfall automatically equals waterlogging, and do NOT falsely claim a trained supervised model.

## Deployed Heuristic Baseline: `ExperimentalMeteorologicalRiskBaseline`

- **Formula**: Combines acute 24-hour rainfall intensity (calibrated against IMD thresholds) and 7-day Antecedent Precipitation Index (API decay=0.85).
- **Scale**: [0.0, 1.0] representing meteorological runoff hazard.
- **Saved Artifact**: `models/rainfall/experimental_risk_baseline.joblib`
- **Feature Schema**: `models/rainfall/feature_schema.json`

## Requirements for Future Supervised Model Training

1. Ingest municipal incident records or police traffic waterlogging advisories into `data/manifests/waterlogging_event_template.csv`.
2. Execute `python scripts/build_event_dataset.py --events <file.csv>` to associate each incident with antecedent rainfall.
3. Re-run `python scripts/train_rainfall_model.py` to train and compare Logistic Regression, Random Forest, and XGBoost.
