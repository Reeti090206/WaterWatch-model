# IndiaScene365 Verified Negative Road Dataset Curation Report

## 1. Executive Summary
- **Source Dataset**: IndiaScene365 (Mendeley Data, DOI: [10.17632/pwffhg6nhz.2](https://data.mendeley.com/datasets/pwffhg6nhz/2))
- **License & Attribution**: Creative Commons Attribution 4.0 International (CC BY 4.0)
- **Total Raw Files in Archive**: 1002
- **Unique Images Evaluated**: 736
- **Exact Duplicates Removed**: 266
- **Overlap with Existing Positive Dataset**: 0 (Zero contamination / data leakage)
- **Quality Rejected**: 160 images (severe blur, extreme dark, or whiteout)
- **Flagged as Ambiguous / Manual Review**: 21 images (potential wet puddles or glare)
- **Verified Non-Waterlogged Candidates**: 555 images
- **Selected for Integration**: 320 verified negative images

## 2. Selection Methodology & Scientific Integrity
- **Rigorous Class Definition**:
  - `waterlogged`: Roadway with visible standing water, submerged surface, or flooding.
  - `not_waterlogged`: Clear or wet roadway WITHOUT visible standing water or pooling puddles.
- **No-Rain Assumption Avoidance**: Rain-conditioned scenes were individually screened. Rainy scenes showing windshield droplets or potential pooling were strictly flagged/excluded rather than assumed dry.
- **Negative Label Formatting**: For YOLOv11 object detection, verified negative images are paired with empty `.txt` label files (0 bounding boxes), teaching the network the visual appearance of clean asphalt, lane markers, and shadows without generating false positive water alarms.

## 3. Curated Sample Breakdown
- **Domain `day`**: 320 images

## 4. Sample Curated Records
| Curated Filename | Original Source Path | Domain | Sharpness | Brightness | Status |
| :--- | :--- | :--- | :--- | :--- | :--- |
| `neg_indiascene_0001_4747.png` | `IndiaScene365/Indiascene365/Day2fog/foggy/Test B/4747.png` | `day` | 377.36 | 81.57 | **VERIFIED NEGATIVE** |
| `neg_indiascene_0002_4848.png` | `IndiaScene365/Indiascene365/Day2fog/foggy/Test B/4848.png` | `day` | 333.97 | 80.35 | **VERIFIED NEGATIVE** |
| `neg_indiascene_0003_3737.png` | `IndiaScene365/Indiascene365/Day2fog/foggy/Test B/3737.png` | `day` | 303.97 | 78.99 | **VERIFIED NEGATIVE** |
| `neg_indiascene_0004_4646.png` | `IndiaScene365/Indiascene365/Day2fog/foggy/Test B/4646.png` | `day` | 276.3 | 84.15 | **VERIFIED NEGATIVE** |
| `neg_indiascene_0005_3838.png` | `IndiaScene365/Indiascene365/Day2fog/foggy/Test B/3838.png` | `day` | 268.73 | 87.03 | **VERIFIED NEGATIVE** |
| `neg_indiascene_0006_174174.png` | `IndiaScene365/Indiascene365/Day2fog/foggy/Train B/174174.png` | `day` | 267.43 | 64.7 | **VERIFIED NEGATIVE** |
| `neg_indiascene_0007_4949.png` | `IndiaScene365/Indiascene365/Day2fog/foggy/Test B/4949.png` | `day` | 262.45 | 79.74 | **VERIFIED NEGATIVE** |
| `neg_indiascene_0008_5050.png` | `IndiaScene365/Indiascene365/Day2fog/foggy/Test B/5050.png` | `day` | 259.86 | 93.14 | **VERIFIED NEGATIVE** |
| `neg_indiascene_0009_4141.png` | `IndiaScene365/Indiascene365/Day2fog/foggy/Test B/4141.png` | `day` | 246.59 | 93.11 | **VERIFIED NEGATIVE** |
| `neg_indiascene_0010_4242.png` | `IndiaScene365/Indiascene365/Day2fog/foggy/Test B/4242.png` | `day` | 244.05 | 89.72 | **VERIFIED NEGATIVE** |
| `neg_indiascene_0011_4343.png` | `IndiaScene365/Indiascene365/Day2fog/Day/Test A/4343.png` | `day` | 231.58 | 105.69 | **VERIFIED NEGATIVE** |
| `neg_indiascene_0012_3636.png` | `IndiaScene365/Indiascene365/Day2fog/foggy/Test B/3636.png` | `day` | 231.2 | 78.49 | **VERIFIED NEGATIVE** |
