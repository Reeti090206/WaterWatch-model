# WaterWatch AI — Nagpur Geographic Generalisation & Transferability Assessment

**Assessment Date**: 2026-10-22  
**Target Domain**: Nagpur Metropolitan Area (NMC), Maharashtra, India  
**Target Basin**: Nag, Pili, and Pora River Catchments (Kanhan-Wainganga Sub-basin)  

---

## 1. Domain Shift & Training Data Audit

| Dimension | Current Project Data Domain | Nagpur Target Operational Domain | Domain Shift Impact |
| :--- | :--- | :--- | :--- |
| **Image Dataset Origin** | Generic web-sourced road photos (Roboflow & Kaggle). 0 EXIF geolocations or timestamps. | Nagpur urban roads, arterial junctions, flyover underpasses, and ward lanes. | **High Visual Shift**: Distinct road construction (cement white-topping vs asphalt), specific roadside drainage layouts, unique local vehicle fleet (e.g. e-rickshaws, two-wheelers). |
| **Daily Rainfall Coverage** | 121,904 observations across 33 districts in Maharashtra (2021–2025). | 1,468 observations across 9 rural/semi-urban stations (`Bazargaon`, `Hardoli`, `Kamtheekhairi`, `Kanholibara`, `Kuhi`, `Ramtek`, `Sadeshwar`, `Tembhurdoh`, `Wadgaon`). | **Moderate Spatial Shift**: Good historical daily records for outer Nagpur district, but lacks dense sub-kilometer automated stations within inner NMC municipal wards. |
| **Hourly Telemetry Coverage** | 22,590 valid hourly measurements across 58 CWC stations in Maharashtra. | **0 stations in Nagpur** in the CWC telemetry export. 3 historical SW sample rows (1991–2020). | **Severe Temporal Shift**: Real-time hourly cloudburst detection cannot rely on existing CWC CSVs for Nagpur; localized sub-daily telemetry is required. |
| **Incident Ground Truth** | **0 verified waterlogging event records**. | Historical disaster cell logs from NMC and Nagpur Traffic Police. | **Unsupervised State**: No verified supervised rainfall-to-flood relationship can be claimed for Nagpur until municipal logs are ingested. |

---

## 2. Specific Physical & Urban Hydrology of Nagpur

Nagpur features unique hydrological and infrastructural characteristics that preclude applying generic out-of-domain models without localized calibration:

1. **River Basin Drainage Network**:
   Nagpur's stormwater runoff discharges into three natural urban streams:
   - **Nag River** (originating from Ambazari Lake overflow, traversing central Nagpur).
   - **Pili River** (northern catchment draining into Kanhan River).
   - **Pora River** (southern catchment draining into Wainganga system).
   When water levels in Nag and Pili rivers rise, stormwater outfalls experience backwater conditions, causing prolonged street waterlogging even after rainfall ceases.

2. **Chronic Low-Lying Vulnerability Hotspots**:
   - **Railway Underpasses**: Narendra Nagar underpass, Manish Nagar underpass, Pardi underpass, Anand Talkies underbridge. These concave structures accumulate runoff rapidly ($>50\text{ cm}$ within 30 minutes of convective showers).
   - **Low-Lying Residential/Commercial Pockets**: Sitabuldi market area, Dhantoli, Besa-Pipla road, Hudkeshwar, Wardhaman Nagar.

3. **Convective Monsoon Dynamics**:
   Nagpur (Vidarbha region) experiences intense localized convective rainstorms during the Southwest Monsoon (June–September), characterized by short-duration, high-intensity cloudburst bursts ($>40\text{ mm/hr}$) which overwhelm surface drainage capacity (designed for $20-25\text{ mm/hr}$).

---

## 3. Required Additional Data for Genuine Nagpur Deployment

To transition from the current experimental baseline to a verified, deployed production system for Nagpur, the following specific datasets must be collected:

1. **Municipal Waterlogging Incident Logs**:
   - Source: Nagpur Municipal Corporation (NMC) Disaster Management Control Room & 100/112 Emergency Police Call Logs.
   - Required Attributes: Exact geographic coordinates, onset timestamp, recession timestamp, measured flood depth ($\text{cm}$), road closures, and pump deployment logs.
   - Format: Ingested via `scripts/annotate_event.py` using `data/manifests/waterlogging_event_template.csv`.

2. **Localized Sub-Daily Weather Station Telemetry**:
   - IMD Nagpur Sonegaon Airport AWS (hourly temperature, precipitation, humidity, pressure).
   - NMC Smart City Ward AWS network (automated rain gauges distributed across all 10 administrative zones).
   - Maharashtra State Agriculture Department (MahaAgri) automated telemetry stations in Nagpur talukas.

3. **Curated Nagpur Road Visual Benchmark**:
   - Collection of $\ge 250$ real Nagpur road images captured during monsoon downpours across diverse lighting (bright daylight, overcast, twilight, night streetlights) and varied road textures (cement white-topping, asphalt, water-filled potholes).
   - Ingestion of Smart City (NSSCDCL) traffic surveillance camera frames at key junction outfalls.

---

## 4. Spatiotemporal Evaluation Strategy for Regional Generalisation

To rigorously test whether models transfer to Nagpur without data leakage or overfitting:

1. **Leave-One-District-Out (LODO) Spatial Cross-Validation**:
   - Train tabular models on other Maharashtra districts (e.g. Pune, Mumbai, Nashik, Kolhapur, Chhatrapati Sambhajinagar).
   - Evaluate exclusively on Nagpur district stations (`Bazargaon`, `Kuhi`, `Kamtheekhairi`, etc.).
   - Report generalization error ($\Delta \text{F1}$, $\Delta \text{Brier}$) to verify spatial transferability across differing agro-climatic zones.

2. **Temporal Out-of-Sample Hold-Out Split**:
   - Train on historical monsoon seasons (2021–2023).
   - Validate on 2024 monsoon.
   - Test on held-out 2025 observations.
   - Strict ban on random train/test shuffling to prevent temporal autocorrelation leakage.

3. **Independent Local Image Testing**:
   - The YOLOv11 detector must achieve $\text{Precision} \ge 0.70$ and $\text{Recall} \ge 0.60$ on real Nagpur road photos before any automated operational dispatch status is claimed.
