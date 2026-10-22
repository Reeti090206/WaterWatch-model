# WaterWatch AI — Regional Waterlogging Machine Learning Pipeline

> **Scope**: Standalone machine learning and hydrometeorological data-processing pipeline for waterlogging risk estimation in **Maharashtra, India**, with dedicated focus on **Nagpur District**.

---

## 1. Executive Summary & Scientific Integrity Statement

### Supervised Rainfall Model Status
- **Current Feasibility**: **Unsupervised / Unlinked** (No verified ground-truth municipal waterlogging incident logs exist in the raw datasets).
- **Explanation**: The available rainfall records (`rainfall_manual_daily_maharashtra_sw_mh_2021_2025.csv`, `rainfall_tel_hr_cwc_mh_2021_2025.csv`, etc.) contain physical precipitation observations (mm) but **no municipal waterlogging incident logs, traffic police blockage reports, or citizen disaster tickets**.
- **Image Datasets**: The Roboflow YOLOv11 and Kaggle Roadway Flooding datasets contain road photographs with visual waterlogging annotations, but **contain zero capture timestamps, GPS coordinates, or links to weather stations**.
- **Strict Anti-Fabrication Compliance**: In accordance with rigorous scientific standards, **no synthetic waterlogging labels have been fabricated**, and rainfall amount is **not falsely equated with waterlogging ground truth**. Instead:
  1. A complete, production-grade rainfall processing and rolling feature-engineering pipeline has been built.
  2. A formal 15-field JSON schema (`waterlogging_event_schema.json`), documented CSV template (`waterlogging_event_template.csv`), annotation CLI (`scripts/annotate_event.py`), and validation auditor (`scripts/validate_events.py`) are established to collect and link future municipal event logs.
  3. A transparent, physics/meteorology-grounded baseline (`ExperimentalMeteorologicalRiskBaseline`) has been established and serialized, combining acute intensity (IMD thresholds) with antecedent soil moisture (7-day API).
  4. Tabular supervised training pipelines (comparing Logistic Regression, Random Forest, and HistGradientBoosting with chronological & spatial cross-validation) stand ready to train automatically once genuine incident labels are ingested.

### Supporting Model (Visual Detection)
- An Ultralytics **YOLOv11** object detection model is trained and evaluated to detect visible waterlogging in street images.
- **Architectural Separation**: The image model is a supporting visual ground-truth verification component; it operates independently of the primary meteorological rainfall prediction pipeline. Probabilities are **not** blended using arbitrary hardcoded formulas.

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
│   └── manifests/                # Event & image schemas, collection templates
│       ├── waterlogging_event_schema.json
│       ├── waterlogging_image_schema.json
│       ├── waterlogging_event_template.csv
│       └── waterlogging_event_template_documentation.md
├── models/
│   ├── rainfall/                 # Feature schema & baseline estimator
│   │   ├── feature_schema.json
│   │   └── experimental_risk_baseline.joblib
│   └── image/                    # Trained YOLOv11 weights
│       └── best.pt
├── reports/                      # Comprehensive technical audits and summaries
│   ├── dataset_inventory_report.md
│   ├── rainfall_feature_definitions.md
│   ├── rainfall_data_quality_report.csv
│   ├── station_catalog.csv
│   ├── station_coverage_summary.csv
│   ├── event_validation_and_linkage_report.md
│   ├── image_model_audit_and_tuning.md
│   ├── image_model_evaluation.json
│   ├── nagpur_generalization_assessment.md
│   ├── rainfall_model_training_report.md
│   ├── rainfall_model_evaluation_summary.csv
│   └── waterwatch_ml_pipeline_report.md
├── scripts/
│   ├── inspect_data.py           # Dataset audit & spatiotemporal linkage check
│   ├── prepare_rainfall.py       # Daily/hourly data cleaning & station catalog
│   ├── build_rainfall_features.py # Rolling temporal windows (1h,3h,6h,24h,72h,API)
│   ├── annotate_event.py         # Ground-truth event annotation and data entry CLI
│   ├── validate_events.py        # Event schema validation and rainfall linkage auditor
│   ├── build_event_dataset.py    # Spatiotemporal matcher linking events to weather
│   ├── train_rainfall_model.py   # Supervised tabular training or baseline serialization
│   ├── evaluate_rainfall_model.py # Regional & intensity-stratified risk evaluation
│   ├── predict_rainfall.py       # Standalone rainfall inference CLI
│   ├── prepare_images.py         # YOLO archive extraction, split & data.yaml generation
│   ├── train_image_model.py      # Ultralytics YOLOv11 training pipeline
│   ├── evaluate_image_model.py   # Evaluation on held-out test split (mAP, P, R)
│   ├── predict_image.py          # Standalone image inference CLI
│   ├── combined_pipeline.py      # Dual-modality inference & disagreement auditor
│   └── rainfall_model_utils.py   # Shared baseline estimators and feature definitions
├── tests/
│   ├── test_images.py            # Image paths, bbox formats, leak checks, inference
│   ├── test_rainfall.py          # Rainfall cleaning, timestamps, null preservation
│   ├── test_features_and_models.py # Feature sets, risk score bounds, monotonicity
│   └── test_waterwatch_pipeline.py # End-to-end integration, error bounds & disagreement flags
├── requirements.txt              # Pipeline dependencies
├── .gitignore                    # Prevents dataset or model binaries from git commit
└── README.md
```

---

## 3. Dataset Inventory Summary

| Dataset Source | Format / Size | Records / Images | Coverage | Scientific Notes |
|---|---|---|---|---|
| **Roboflow Water Logging** | YOLOv11 ZIP (7.9 MB) | 199 images, 466 bboxes | Single class: `water_logging` | Split into Train (139), Val (39), Test (21). Zero background images in raw set. No GPS/timestamps. |
| **Kaggle Roadway Flooding** | ZIP (16.8 MB) | 441 images, 441 masks | 512x384 Binary PNG masks | Semantic segmentation dataset. No GPS/timestamps. |
| **Daily Manual Rainfall** | CSV (19.6 MB) | 119,522 clean rows (2021–2025) | 33 Districts, 658 Stations | Nagpur: 1,468 records across 9 stations. Daily 08:30 IST observations. |
| **Hourly Telemetry CWC** | CSV (36.7 MB) | 266,707 total rows (2021–2025) | 22 Districts, 58 Stations | 244,117 rows (91.5%) missing telemetry. Missing intervals preserved as NaN (never zero). |
| **Historical Telemetry SW** | CSV (37.1 KB) | 268 rows (1991–2020) | 8 Districts, 10 Stations | Historical sample observations. |

---

## 4. Setup and Installation

```powershell
pip install -r requirements.txt
```

---

## 5. End-to-End Pipeline Execution

### Step 1: Inspect All Datasets & Audit Linkage
```powershell
python scripts/inspect_data.py
```

### Step 2: Clean and Normalize Rainfall Datasets
```powershell
python scripts/prepare_rainfall.py
```

### Step 3: Compute Multi-Scale Rolling Features (1h, 3h, 6h, 24h, 72h, API)
```powershell
python scripts/build_rainfall_features.py
```

### Step 4: Event Label Ingestion, Annotation & Validation
```powershell
# 1. Interactive or scripted event data entry:
python scripts/annotate_event.py --event_id "WW-NGP-2024-001" --location_id "NGP-SITABULDI-01" --lat 21.1458 --lon 79.0882 --start "2024-07-22T14:30:00+05:30" --observed 1 --severity "Severe" --depth_cm 45.0 --evidence "Municipal_Log" --source "Nagpur Municipal Corporation" --status "Verified_Official" --annotator "OP-NMC-101"

# 2. Validate events CSV against schema and check weather station matching:
python scripts/validate_events.py --events "data/manifests/waterlogging_event_template.csv" --max_dist_km 25.0

# 3. Match verified events to preceding meteorological conditions:
python scripts/build_event_dataset.py --events "data/manifests/waterlogging_event_template.csv"
```

### Step 5: Train Rainfall Model or Serialize Risk Baseline
```powershell
python scripts/train_rainfall_model.py
```

### Step 6: Evaluate Rainfall Model Across Maharashtra & Nagpur
```powershell
python scripts/evaluate_rainfall_model.py
```

### Step 7: Prepare Image Dataset & Split YOLO Annotations
```powershell
python scripts/prepare_images.py
```

### Step 8: Train YOLOv11 Waterlogging Detection Model
```powershell
# Fast CPU verification:
python scripts/train_image_model.py --epochs 5 --batch 8 --model yolo11n.pt

# Full training:
python scripts/train_image_model.py --epochs 30 --batch 16
```

### Step 9: Evaluate Image Model on Held-Out Test Set
```powershell
python scripts/evaluate_image_model.py --split test
```

---

## 6. Standalone Inference Engines

### 1. Standalone Rainfall Risk Inference
Run risk estimation for any arbitrary rainfall observation or scenario:
```powershell
# Heavy monsoon scenario in Nagpur:
python scripts/predict_rainfall.py --rainfall_mm 85.0 --prev1_mm 40.0 --prev2_mm 20.0 --location "Nagpur"

# JSON output mode:
python scripts/predict_rainfall.py --rainfall_mm 12.0 --location "Pune" --json
```

### 2. Standalone Image Waterlogging Detection
Run visual detection on single images or entire directories:
```powershell
# Inference with annotated image export:
python scripts/predict_image.py --source "data/processed/yolo_water_logging/images/test/waterloggingt-105-_jpg.rf.982f24e5c60290f4b23ab7b6fbf49db6.jpg" --conf 0.20 --save

# JSON output mode:
python scripts/predict_image.py --source "data/processed/yolo_water_logging/images/test" --conf 0.25 --json
```

### 3. Combined Dual-Modality Prediction & Disagreement Verification
Evaluate both hydrometeorological hazard and optical ground verification simultaneously:
```powershell
python scripts/combined_pipeline.py --rainfall_mm 95.0 --prev1_mm 50.0 --image "data/processed/yolo_water_logging/images/test/waterloggingt-105-_jpg.rf.982f24e5c60290f4b23ab7b6fbf49db6.jpg" --location "Nagpur - Sitabuldi" --conf 0.20 --save
```

---

## 7. Running Automated Test Suite

Execute all 24 unit and integration tests across the complete pipeline:
```powershell
pytest tests/ -v
```

Tests verify:
- Non-zero preservation of telemetry nulls.
- Monotonicity of hydrological risk scores.
- Anti-leakage temporal rolling windows (1h, 3h, 6h, 24h, 72h).
- Event schema rejection of invalid coordinates, timestamps, and enums.
- Standalone inference output schemas.
- Combined pipeline consensus and disagreement flagging.
