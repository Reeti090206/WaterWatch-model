# WaterWatch AI — Regional Waterlogging Machine Learning Pipeline

> **Scope**: Standalone machine learning and hydrometeorological data-processing pipeline for waterlogging risk estimation in **Maharashtra, India**, with dedicated focus on **Nagpur District**.

---

## 1. Executive Summary & Scientific Integrity Statement

### Supervised Rainfall Model Status
- **Current Feasibility**: **Unsupervised / Unlinked** (No ground-truth event labels exist in the raw datasets).
- **Explanation**: The available rainfall records (`rainfall_manual_daily_maharashtra_sw_mh_2021_2025.csv`, `rainfall_tel_hr_cwc_mh_2021_2025.csv`, etc.) contain physical precipitation observations (mm) but **no municipal waterlogging incident logs, traffic police blockage reports, or citizen disaster reports**.
- **Image Datasets**: The Roboflow YOLOv11 and Kaggle Roadway Flooding datasets contain road photographs with visual waterlogging annotations, but **contain zero capture timestamps, GPS coordinates, or links to weather stations**.
- **Mandate**: In accordance with rigorous scientific standards, **no synthetic waterlogging labels have been fabricated**, and rainfall amount is **not falsely equated with waterlogging ground truth**. Instead:
  1. A complete, production-grade rainfall processing and rolling feature-engineering pipeline has been built.
  2. A formal JSON schema and ingestion workflow (`scripts/build_event_dataset.py`) are established to link future municipal event logs.
  3. A transparent, physics/meteorology-grounded baseline (`ExperimentalMeteorologicalRiskBaseline`) has been established and serialized, combining acute intensity (IMD thresholds) with antecedent soil moisture (7-day API).

### Supporting Model (Visual Detection)
- An Ultralytics **YOLOv11** object detection model is trained and evaluated to detect visible waterlogging in street images.
- **Architectural Separation**: The image model is a supporting visual component; it is **not** a replacement for the primary meteorological rainfall prediction pipeline.

---

## 2. Directory Structure

```
waterwatch-ml/
├── data/
│   ├── raw/                      # Original raw CSVs and ZIP archives
│   ├── extracted/                # Extracted raw files
│   ├── processed/                # Cleaned datasets and engineered feature matrices
│   │   ├── rainfall_daily_observed.csv
│   │   ├── rainfall_hourly_observed.csv
│   │   ├── rainfall_daily_features.csv
│   │   ├── rainfall_hourly_features.csv
│   │   └── yolo_water_logging/   # Train, Val, Test YOLO dataset & data.yaml
│   └── manifests/                # Event schema and collection templates
│       ├── waterlogging_event_schema.json
│       └── waterlogging_event_template.csv
├── models/
│   ├── rainfall/                 # Feature schema & baseline estimator
│   │   ├── feature_schema.json
│   │   └── experimental_risk_baseline.joblib
│   └── image/                    # Trained YOLOv11 weights
│       └── best.pt
├── reports/                      # Comprehensive technical audits and summaries
│   ├── dataset_inventory_report.md
│   ├── rainfall_data_quality_report.csv
│   ├── station_catalog.csv
│   ├── station_coverage_summary.csv
│   ├── rainfall_model_training_report.md
│   ├── rainfall_model_evaluation_summary.csv
│   └── image_model_evaluation.json
├── scripts/
│   ├── inspect_data.py           # Dataset audit & spatiotemporal linkage check
│   ├── prepare_rainfall.py       # Daily/hourly data cleaning & station catalog
│   ├── build_rainfall_features.py # Rolling temporal windows, API & risk scoring
│   ├── build_event_dataset.py    # Schema generation & spatiotemporal matcher
│   ├── train_rainfall_model.py   # Supervised tabular training or baseline serialization
│   ├── evaluate_rainfall_model.py # Regional & intensity-stratified risk evaluation
│   ├── prepare_images.py         # YOLO archive extraction, split & data.yaml generation
│   ├── train_image_model.py      # Ultralytics YOLOv11 training pipeline
│   ├── evaluate_image_model.py   # Evaluation on held-out test split (mAP, P, R)
│   ├── predict_image.py          # Standalone image inference script
│   └── rainfall_model_utils.py   # Shared baseline estimators and definitions
├── tests/
│   ├── test_images.py            # Image paths, bbox formats, leak checks, inference
│   ├── test_rainfall.py          # Rainfall cleaning, timestamps, null preservation
│   └── test_features_and_models.py # Feature sets, risk score bounds, monotonicity
├── requirements.txt              # Pipeline dependencies
├── .gitignore                    # Prevents dataset or model binaries from git commit
└── README.md
```

---

## 3. Dataset Inventory Summary

| Dataset Source | Format / Size | Records / Images | Coverage | Notes |
|---|---|---|---|---|
| **Roboflow Water Logging** | YOLOv11 ZIP (7.9 MB) | 199 images, 466 bboxes | Single class: `water_logging` | Originally only had `valid/`; pipeline split into Train (139), Val (39), Test (21). No GPS/timestamps. |
| **Kaggle Roadway Flooding** | ZIP (16.8 MB) | 441 images, 441 masks | 512x384 Binary PNG masks | Semantic segmentation dataset. No GPS/timestamps. |
| **Daily Manual Rainfall** | CSV (19.6 MB) | 119,522 clean rows (2021–2025) | 33 Districts, 658 Stations | Nagpur: 1,465 records across 9 stations. Daily 08:30 IST observations. |
| **Hourly Telemetry CWC** | CSV (36.7 MB) | 266,707 total rows (2021–2025) | 22 Districts, 58 Stations | 244,117 rows (91.5%) missing telemetry. Missing intervals preserved (not set to 0). |
| **Historical Telemetry SW** | CSV (37.1 KB) | 268 rows (1991–2020) | 8 Districts, 10 Stations | Sample historical telemetry. |

---

## 4. Setup and Installation

### 1. Install Dependencies
```powershell
pip install -r requirements.txt
```

---

## 5. End-to-End Pipeline Execution

### Step 1: Inspect All Datasets & Generate Audit Reports
```powershell
python scripts/inspect_data.py
```
Outputs:
- `reports/dataset_inventory_report.md`
- `reports/rainfall_data_quality_report.csv`
- `reports/station_catalog.csv`
- `reports/station_coverage_summary.csv`

### Step 2: Clean and Normalize Rainfall Datasets
```powershell
python scripts/prepare_rainfall.py
```
Outputs:
- `data/processed/rainfall_daily_observed.csv`
- `data/processed/rainfall_hourly_observed.csv`

### Step 3: Compute Multi-Scale Rolling Features & Risk Baseline
```powershell
python scripts/build_rainfall_features.py
```
Outputs:
- `data/processed/rainfall_daily_features.csv`
- `data/processed/rainfall_hourly_features.csv`

### Step 4: Audit Event Labels or Match Future Incident Records
```powershell
# To audit existing labels:
python scripts/build_event_dataset.py

# To ingest and link future municipal waterlogging incident logs:
python scripts/build_event_dataset.py --events path/to/verified_events.csv --max_dist_km 25.0
```

### Step 5: Train Rainfall Model or Serialize Risk Baseline
```powershell
python scripts/train_rainfall_model.py
```
Outputs:
- `models/rainfall/feature_schema.json`
- `models/rainfall/experimental_risk_baseline.joblib`
- `reports/rainfall_model_training_report.md`

### Step 6: Evaluate Rainfall Model Across Maharashtra & Nagpur
```powershell
python scripts/evaluate_rainfall_model.py
```
Outputs:
- `reports/rainfall_model_evaluation_summary.csv`

### Step 7: Prepare Image Dataset & Split YOLO Annotations
```powershell
python scripts/prepare_images.py
```
Outputs:
- `data/processed/yolo_water_logging/data.yaml`
- `data/processed/yolo_water_logging/images/{train,val,test}`
- `data/processed/yolo_water_logging/labels/{train,val,test}`

### Step 8: Train YOLOv11 Waterlogging Detection Model
```powershell
# Fast CPU verification (e.g. 5 epochs):
python scripts/train_image_model.py --epochs 5 --batch 8 --model yolo11n.pt

# Full GPU training:
python scripts/train_image_model.py --epochs 30 --batch 16 --device 0
```
Outputs:
- `models/image/best.pt`

### Step 9: Evaluate Image Model on Held-Out Test Set
```powershell
python scripts/evaluate_image_model.py --split test
```
Outputs:
- `reports/image_model_evaluation.json`

### Step 10: Run Standalone Image Inference
```powershell
python scripts/predict_image.py --source "data/processed/yolo_water_logging/images/test" --conf 0.25 --save
```
Returns structured JSON bounding boxes and waterlogging detection flags.

---

## 6. Running Automated Verification Tests

Execute the complete pytest suite:
```powershell
pytest tests/ -v
```

All tests verify image splits, data leakage absence, coordinate ranges, null preservation, feature monotonicity, and model loading.
