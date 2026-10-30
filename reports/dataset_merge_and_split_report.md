# WaterWatch AI — Unified Dataset Merge & Split Report (Phase 4)

## 1. Overview
Integrates verified positive waterlogging scenes with verified negative road scenes from IndiaScene365.
- **Total Dataset Size**: 519 images
- **Positive (Waterlogged)**: 199 images (with explicit YOLO bounding boxes)
- **Negative (Not Waterlogged)**: 320 images (with standard empty YOLO label files)
- **Partitioning Seed**: 42

## 2. Partitioning Breakdown

| Split | Waterlogged (Pos) | Not Waterlogged (Neg) | Total Images | Positive Boxes | Class Ratio (Pos:Neg) |
| :--- | :--- | :--- | :--- | :--- | :--- |
| **Train** | 139 | 224 | 363 | 331 | 1 : 1.61 |
| **Validation** | 29 | 48 | 77 | 67 | 1 : 1.66 |
| **Held-Out Test** | 31 | 48 | 79 | 68 | 1 : 1.55 |
| **Total** | **199** | **320** | **519** | **466** | **1 : 1.61** |

## 3. Storage Formats Generated
1. **YOLOv11 Detection Format**: `data/processed/yolo_water_logging/`
   - `images/{train,val,test}` and `labels/{train,val,test}`
   - Negatives contain clean empty text files to prevent false alarms on dry pavement.
2. **Image Classification Format**: `data/processed/classification_water_logging/`
   - `{train,val,test}/{waterlogged,not_waterlogged}/` for standard computer vision loaders.
