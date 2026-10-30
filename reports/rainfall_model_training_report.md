# WaterWatch AI — Rainfall-to-Waterlogging Model Training Status

## 1. Production Model Status (Verified Municipal Data)

- **Status**: 🔴 **BLOCKED ON DATA**
- **Reason**: Raw telemetry and daily rainfall files do not contain verified municipal waterlogging incident records (timestamps, geolocations, and ground-truth flooded vs non-flooded verification from NMC or traffic police).
- **Integrity Compliance**: No synthetic records are inserted into municipal manifests.
- **Deployed Heuristic Baseline**: `ExperimentalMeteorologicalRiskBaseline` (IMD thresholds + 7-day API).
- **Artifact**: `models/rainfall/experimental_risk_baseline.joblib`

## 2. Experimental Synthetic Model Status

- **Status**: 🟢 **READY (SYNTHETIC_EXPERIMENTAL)**
- **Training Dataset**: `waterwatch_ai_nagpur_localities_sample.csv`
- **Best Model**: `LogisticRegression`
- **Target**: `waterlogging_observed` (binary 0/1)
- **Excluded Features**: `severity` (leakage prevention), `location_id` / `location_name` (memorization prevention)
- **Saved Artifacts**: `models/rainfall/synthetic_rainfall_model.joblib`, `ml/rainfall/rainfall_model.joblib`
- **Evaluation Results (Test Set)**: `{'MajorityBaseline': {'accuracy': 0.7767, 'precision': 0.0, 'recall': 0.0, 'f1_score': 0.0, 'roc_auc': 0.5, 'pr_auc': 0.2233, 'brier_score': 0.2233, 'confusion_matrix': [[233, 0], [67, 0]]}, 'LogisticRegression': {'accuracy': 0.68, 'precision': 0.3739, 'recall': 0.6418, 'f1_score': 0.4725, 'roc_auc': 0.7015, 'pr_auc': 0.4157, 'brier_score': 0.2238, 'confusion_matrix': [[161, 72], [24, 43]]}, 'RandomForest': {'accuracy': 0.7, 'precision': 0.3678, 'recall': 0.4776, 'f1_score': 0.4156, 'roc_auc': 0.667, 'pr_auc': 0.3734, 'brier_score': 0.2064, 'confusion_matrix': [[178, 55], [35, 32]]}, 'HistGradientBoosting': {'accuracy': 0.67, 'precision': 0.3545, 'recall': 0.5821, 'f1_score': 0.4407, 'roc_auc': 0.6638, 'pr_auc': 0.3712, 'brier_score': 0.2179, 'confusion_matrix': [[162, 71], [28, 39]]}}`

## 3. Requirements for Future Verified Production Training

1. Ingest municipal incident records into `data/manifests/waterlogging_event_template.csv`.
2. Execute `python scripts/build_event_dataset.py --events <file.csv>`.
3. Re-run `python scripts/train_rainfall_model.py` to train verified production models.
