# WaterWatch AI — Rainfall-to-Waterlogging ML Pipeline

This subpackage implements the machine learning pipeline for rainfall-based urban waterlogging risk estimation in Nagpur, Maharashtra.

> [!WARNING]
> **Data Provenance & Scientific Integrity Notice**:
> The primary dataset (`waterwatch_ai_nagpur_localities.csv`) uses authentic Nagpur neighborhood names (Dharampeth, Sadar, Sitabuldi, Manish Nagar, Dhantoli, Mankapur). However, **the rainfall readings, drainage proxies, and binary waterlogging labels were synthetically generated**.
> This pipeline is classified as an **experimental synthetic-data baseline**. It is **not** calibrated for municipal emergency dispatch or real-world civic alerting without ground-truth NMC incident logs.

---

## Architecture & File Structure

```
ml/rainfall/
├── __init__.py                        # Package initialization
├── validate_dataset.py               # Data integrity, schema, and monotonic window validator
├── train_rainfall_model.py           # Model training, temporal splitting, and artifact export
├── evaluate_rainfall_model.py        # Independent held-out test evaluation & metrics
├── predict_rainfall.py               # Standalone reusable inference function & CLI demo
├── rainfall_model.joblib             # Fitted StandardScaler + Classifier pipeline
├── model_metadata.json               # Serialized architecture, hyperparams, and test metrics
├── evaluation_report.md              # Markdown test evaluation benchmark report
├── rainfall_dataset_validation_report.md # Markdown dataset audit and leakage report
└── README.md                         # Pipeline documentation (this file)
```

---

## 1. Dataset Validation

Validates column schema, missing values, duplicate timestamp-location pairs, physical monotonicity (`1h <= 3h <= 6h <= 24h`), and target consistency.

```bash
python ml/rainfall/validate_dataset.py --csv waterwatch_ai_nagpur_localities.csv
```

Outputs:
- JSON summary to `ml/rainfall/dataset_validation_summary.json`
- Markdown report to `ml/rainfall/rainfall_dataset_validation_report.md` and `reports/rainfall_dataset_validation_report.md`

---

## 2. Model Training & Comparison

Trains and benchmarks multiple candidate models using a chronological holdout split (70% train, 15% validation, 15% test) to prevent temporal lookahead leakage from multi-hour cumulative rainfall windows.

Models compared:
1. **MajorityBaseline** (`DummyClassifier`)
2. **LogisticRegression** (`StandardScaler`, `class_weight='balanced'`)
3. **RandomForest** (`max_depth=6`, `min_samples_leaf=5`, `class_weight='balanced'`)
4. **HistGradientBoosting** (`max_depth=4`, `learning_rate=0.05`)

```bash
python ml/rainfall/train_rainfall_model.py --csv waterwatch_ai_nagpur_localities.csv
```

Outputs:
- Fitted pipeline serialized to `ml/rainfall/rainfall_model.joblib` and `models/rainfall/best_rainfall_model.joblib`
- Training metadata and schema saved to `ml/rainfall/model_metadata.json`
- Full evaluation benchmark written to `ml/rainfall/evaluation_report.md`

---

## 3. Evaluation on Held-Out Test Data

Computes comprehensive metrics on the unobserved 15% chronological test partition (300 samples: 67 positive, 233 negative):

```bash
python ml/rainfall/evaluate_rainfall_model.py
```

### Measured Performance Benchmark:
| Metric | Baseline (Majority) | LogisticRegression (Best) | RandomForest | HistGradientBoosting |
| :--- | :--- | :--- | :--- | :--- |
| **Accuracy** | 0.7767 | **0.6800** | 0.7000 | 0.6700 |
| **Precision** | 0.0000 | **0.3739** | 0.3684 | 0.3548 |
| **Recall** | 0.0000 | **0.6418** | 0.4776 | 0.5821 |
| **F1-Score** | 0.0000 | **0.4725** | 0.4156 | 0.4407 |
| **ROC-AUC** | 0.5000 | **0.7015** | 0.6672 | 0.6641 |
| **PR-AUC** | 0.2233 | **0.4157** | 0.3734 | 0.3705 |
| **Brier Score** | 0.2233 | **0.2238** | 0.2195 | 0.2312 |

---

## 4. Standalone Prediction & CLI Inference

### Programmatic Python API:
```python
from ml.rainfall.predict_rainfall import predict_waterlogging

input_telemetry = {
    "rainfall_1h_mm": 28.5,
    "rainfall_3h_mm": 52.0,
    "rainfall_6h_mm": 74.0,
    "rainfall_24h_mm": 98.0,
    "rainfall_prev_72h_mm": 130.0,
    "drainage_capacity_proxy": 0.35
}

result = predict_waterlogging(input_telemetry)
print("Predicted:", result["waterlogging_predicted"])
print("Model Score:", result["model_score"])
print("Risk Category:", result["risk_category"])
```

### CLI Command Demo:
```bash
# High risk scenario
python ml/rainfall/predict_rainfall.py --rain-1h 35.0 --rain-3h 60.0 --rain-6h 80.0 --rain-24h 110.0 --rain-72h 150.0 --drainage-proxy 0.30

# Low risk scenario
python ml/rainfall/predict_rainfall.py --rain-1h 0.0 --rain-3h 2.0 --rain-6h 5.0 --rain-24h 10.0 --rain-72h 15.0 --drainage-proxy 0.80
```

---

## 5. Prevented Data Leakage & Engineering Safeguards

- **Strict Exclusion of `severity`**: `severity` is assigned only when an incident occurs. Including it creates 100% label leakage.
- **Strict Exclusion of `location_id` / `location_name`**: Prevents one-hot memorization of historical locality incidence frequencies.
- **Strict Monotonic Validation**: Validates that cumulative rainfall accumulation increases monotonically with window length.
- **No Hardcoded Silent Fallbacks**: If model artifacts are missing or corrupted, a `ModelLoadError` is raised rather than fabricating a false prediction.
