# WaterWatch AI — Rainfall Dataset Validation Report

**Dataset File**: `waterwatch_ai_nagpur_localities_sample.csv`  
**Total Records**: `2000`  
**Validation Status**: `PASSED`  

---

## 1. Executive Summary & Provenance Disclosure

> [!IMPORTANT]
> **Synthetic Demonstration Data Notice**: Although this dataset features genuine Nagpur locality names (e.g., Dharampeth, Sadar, Sitabuldi, Manish Nagar, Dhantoli, Mankapur), the rainfall accumulation figures, drainage capacity proxies, and waterlogging occurrence labels were **synthetically generated**. They do NOT represent verified observations from Nagpur Municipal Corporation (NMC) or IMD.

---

## 2. Schema and Completeness

- **Expected Columns**: 11  
- **Present Columns**: 11  
- **Missing Columns**: []  
- **Null / Missing Value Count**: 0 (100% complete records)

| Column | Type / Role | Null Count |
| :--- | :--- | :--- |
| `timestamp` | Metadata | 0 |
| `location_id` | Metadata | 0 |
| `location_name` | Metadata | 0 |
| `rainfall_1h_mm` | Input Feature | 0 |
| `rainfall_3h_mm` | Input Feature | 0 |
| `rainfall_6h_mm` | Input Feature | 0 |
| `rainfall_24h_mm` | Input Feature | 0 |
| `rainfall_prev_72h_mm` | Input Feature | 0 |
| `drainage_capacity_proxy` | Input Feature | 0 |
| `waterlogging_observed` | Target | 0 |
| `severity` | Leaked Outcome | 0 |

---

## 3. Rainfall Window Consistency (Monotonic Integrity)

Physical rainfall accumulations over overlapping windows must strictly satisfy:  
`rainfall_1h_mm <= rainfall_3h_mm <= rainfall_6h_mm <= rainfall_24h_mm`

- **1h > 3h Violations**: `0`
- **3h > 6h Violations**: `0`
- **6h > 24h Violations**: `0`
- **Monotonic Integrity Assessment**: `PERFECT (100% Valid)`

---

## 4. Value Ranges & Units

| Feature | Min (mm or index) | Median | Max (mm or index) | Units / Scale |
| :--- | :--- | :--- | :--- | :--- |
| `rainfall_1h_mm` | `0.0` | `3.59` | `54.8` | Millimeters (mm) |
| `rainfall_3h_mm` | `0.1` | `11.14` | `59.1` | Millimeters (mm) |
| `rainfall_6h_mm` | `1.4` | `22.24` | `79.4` | Millimeters (mm) |
| `rainfall_24h_mm` | `3.8` | `42.39` | `113.4` | Millimeters (mm) |
| `rainfall_prev_72h_mm` | `12.4` | `79.86` | `206.3` | Millimeters (mm) |
| `drainage_capacity_proxy` | `0.12` | `0.59` | `0.95` | Unitless [0, 1] |

---

## 5. Class Distribution & Imbalance

- **Class 0 (No Waterlogging)**: `1537` (76.85%)  
- **Class 1 (Waterlogged Observed)**: `463` (23.15%)  
- **Imbalance Ratio**: approximately `3.32 : 1`  
- **Mitigation in Modeling**: Models must use `class_weight='balanced'` and be evaluated via Precision-Recall AUC (PR-AUC) and F1-score rather than simple classification accuracy.

---

## 6. Duplicates and Conflicting Observations

- **Exact Row Duplicates**: `0`  
- **Repeated (timestamp, location_id) Pairs**: `106`  
- **Conflicting Outcome Groups**: `35` groups where identical timestamp and location had conflicting waterlogging labels (both 0 and 1).  
- **Resolution Strategy**: When training models, these conflicting pairs are resolved by prioritizing the verified positive record or deduplicating to eliminate contradictory training signals.

---

## 7. Data Leakage & Feature Selection Policy

1. **`severity` Excluded**: `severity` represents post-event damage level ('low', 'moderate', 'high') and is derived directly from the occurrence. Using it as a predictor would constitute 100% target leakage.
2. **`location_id` / `location_name` Excluded**: Memorizing specific locality IDs produces brittle models that cannot generalize across Nagpur. Features must rely solely on meteorological measurements and generalized drainage proxies.
3. **`drainage_capacity_proxy` Handled Cautiously**: Acknowledged as a synthetic demonstration parameter rather than calibrated civil infrastructure flow capacity.
