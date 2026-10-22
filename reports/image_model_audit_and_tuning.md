# WaterWatch AI — Image Model Investigation, Annotation Audit & Evaluation Report

**Model Architecture**: YOLOv11 Nano (`yolo11n`)  
**Weights Artifact**: `models/image/best.pt`  
**Dataset**: Roboflow Water Logging Dataset (`data/processed/yolo_water_logging`)  
**Primary Task**: Single-Class Object Detection (`water_logging`)  

---

## 1. Dataset Annotation & Class Audit

- **Total Extracted Images**: 199 images (512x384 and 640x640 resolutions)
- **Split Distribution**:
  - `train`: 139 images, 331 bounding boxes
  - `val`: 39 images, 89 bounding boxes
  - `test`: 21 images, 46 bounding boxes
- **Unique Hash Audit**: Zero duplicate images detected across splits (199 distinct SHA-256 hashes).
- **Target Classes**: Exactly 1 class (`water_logging`, Class ID 0).
- **Critical Finding on Annotation Distribution**:
  - **Background / Negative Images**: **0 out of 199 images** (0.0%).
  - Every single image in the Roboflow export contains at least one positive bounding box.
  - **Engineering Risk**: Detectors trained exclusively on positive instances develop a severe inductive bias, leading to elevated false-positive rates when processing dry roadways, wet asphalt reflections, or shadowed pavements in the wild. Future iterations must introduce at least 20–30% verified dry road negative control images.

---

## 2. Held-Out Test Evaluation Benchmark

Evaluated on the independent test set (21 images, 46 ground-truth instances) at image size 640:

| Metric | Measured Value | Standard Benchmark Interpretation |
| :--- | :--- | :--- |
| **Precision (B)** | `0.4219` | 42.2% of proposed bounding boxes accurately overlap ground-truth waterlogging. |
| **Recall (B)** | `0.1739` | 17.4% of total annotated waterlogging regions are successfully recalled at IoU 0.50. |
| **mAP@0.50** | `0.1950` | Mean Average Precision at IoU threshold 0.50. |
| **mAP@0.50:0.95** | `0.0929` | Mean Average Precision across IoU thresholds 0.50 to 0.95. |
| **Inference Latency** | `82.2 ms / image` | Measured on 12th Gen Intel Core i5 CPU (`torch 2.14.1+cpu`). |

### Root-Cause Analysis for Low Metrics:
1. **Low Sample Size**: Only 139 training images were available. Object detection models typically require $\ge 1,500$ diverse instances for robust generalization.
2. **Diffuse Puddle Boundaries**: Puddles and shallow roadway sheen lack rigid geometric edges (unlike vehicles or pedestrians). Annotators draw bounding boxes with high subjectivity—some boxing individual small ripples, others boxing the entire street width.
3. **Severe Recall Penalty at High IoU**: Because water boundaries are amorphous, box coordinates frequently fail the IoU $> 0.50$ intersection requirement even when the detector correctly identifies the presence of water.

---

## 3. Operational Confidence Threshold Recommendations

| Operational Context | Recommended Threshold | Rationale |
| :--- | :--- | :--- |
| **High Sensitivity Alerting (Early Warning)** | `conf = 0.15 - 0.20` | Maximizes recall to catch subtle early pooling on roadway shoulders before traffic obstruction occurs. |
| **Standard Automated Ingestion** | `conf = 0.25` | Balances true positives while filtering low-confidence pavement reflections. |
| **High Specificity Dispatch (Emergency Response)** | `conf = 0.40+` | Ensures high bounding box certainty before dispatching municipal drainage pumps. |

---

## 4. Why Severity & Depth Cannot Be Inferred from Bounding Boxes

1. **2D Projection vs 3D Volume**:
   A 2D bounding box measures pixel area $(w \times h)$, not water column depth $(\text{cm})$. A 2-meter wide puddle of $1\text{ cm}$ depth appears visually identical or larger than a narrow $50\text{ cm}$ deep pothole.
2. **Lack of Calibrated Ground Markers**:
   Depth can only be quantitatively measured if physical markers (curb heights, vehicle wheel submergence, or painted staff gauges) are segmented and calibrated.
3. **Future Work Roadmap**:
   - Implement semantic segmentation using the Kaggle Roadway Flooding masks (`archive.zip`) to calculate water surface area percentage.
   - Collect stratified multi-tier incident photos categorized into `Low` ($<15\text{ cm}$), `Moderate` ($15-30\text{ cm}$), and `Severe` ($>30\text{ cm}$) to train a dedicated ordinal severity classifier.
