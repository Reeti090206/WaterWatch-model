# WaterWatch AI — Rainfall-to-Waterlogging Model Evaluation Report

**Best Model**: `LogisticRegression` (`LogisticRegression`)  
**Model Version**: `1.0.0-synthetic`  
**Data Provenance**: `SYNTHETIC_EXPERIMENTAL`  
**Split Strategy**: `Chronological Holdout (70/15/15) to prevent rolling window leakage`  

---

## 1. Scientific Integrity & Model Limitations

> [!WARNING]
> **Notice of Synthetic Data Limitation**: This model was trained on `waterwatch_ai_nagpur_localities.csv`. While locality identifiers correspond to genuine Nagpur neighborhoods (Dharampeth, Sadar, Sitabuldi, etc.), the rainfall measurements, drainage proxies, and binary waterlogging labels were synthetically generated. Consequently, the model learns the **synthetic labeling rules**, not real-world urban runoff dynamics. This model is **NOT calibrated for operational civic alerting** and must be labeled strictly as an **experimental synthetic-data baseline**.

---

## 2. Test Set Evaluation Benchmark (Chronological Holdout)

- **Train Samples**: `1400`  
- **Validation Samples**: `300`  
- **Held-Out Test Samples**: `300`  
- **Test Class Balance**: Positive=22.3%, Negative=77.7%

| Model Algorithm | Accuracy | Precision | Recall | F1-Score | ROC-AUC | PR-AUC | Brier Score |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| **MajorityBaseline** | `0.7767` | `0.0000` | `0.0000` | `0.0000` | `0.5000` | `0.2233` | `0.2233` |
| **LogisticRegression** | `0.6800` | `0.3739` | `0.6418` | `0.4725` | `0.7015` | `0.4157` | `0.2238` |
| **RandomForest** | `0.7000` | `0.3678` | `0.4776` | `0.4156` | `0.6670` | `0.3734` | `0.2064` |
| **HistGradientBoosting** | `0.6700` | `0.3545` | `0.5821` | `0.4407` | `0.6638` | `0.3712` | `0.2179` |

---

## 3. Confusion Matrix for Best Model (`LogisticRegression`)

| | Predicted Non-Waterlogged (0) | Predicted Waterlogged (1) |
| :--- | :--- | :--- |
| **Actual Non-Waterlogged (0)** | `161` (TN) | `72` (FP) |
| **Actual Waterlogged (1)** | `24` (FN) | `43` (TP) |

---

## 4. Feature Importance & Coefficients

| Feature | Role / Importance | Hydrological Meaning |
| :--- | :--- | :--- |
| `rainfall_1h_mm` | `0.3854` | Acute 1-hour rainfall accumulation in mm |
| `rainfall_3h_mm` | `0.2286` | Cumulative 3-hour rainfall accumulation in mm |
| `rainfall_6h_mm` | `-0.0211` | Cumulative 6-hour rainfall accumulation in mm |
| `rainfall_24h_mm` | `0.0486` | Cumulative 24-hour rainfall accumulation in mm |
| `rainfall_prev_72h_mm` | `0.1567` | Antecedent 72-hour soil saturation rainfall in mm |
| `drainage_capacity_proxy` | `-0.3733` | Synthetic locality runoff clearance rate (index in [0.0, 1.0]) |

---

## 5. Prevented Target Leakage

- **`severity` completely omitted**: `severity` is assigned only when an event occurs, encoding direct post-hoc labels.
- **`location_id` / `location_name` omitted**: Models trained on locality dummy codes memorize locality frequency rather than physical rainfall-runoff mechanics.
- **Chronological Temporal Split**: Prevents overlapping rolling rainfall windows (3h, 6h, 24h, 72h) from leaking into future test intervals.