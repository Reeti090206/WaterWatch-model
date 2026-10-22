# WaterWatch AI — Waterlogging Event Template & Ingestion Documentation

**Document**: `data/manifests/waterlogging_event_template_documentation.md`  
**Template File**: `data/manifests/waterlogging_event_template.csv`  
**JSON Schema**: `data/manifests/waterlogging_event_schema.json`  

---

## 1. Column Specifications

| Column Name | Type | Mandatory? | Allowed Values / Format | Description & Scientific Rules |
| :--- | :--- | :--- | :--- | :--- |
| `event_id` | String | Yes | Alphanumeric (`[A-Za-z0-9_-]+`) | Unique identifier for incident or survey point (e.g. `WW-NGP-2024-001`). |
| `location_id` | String | Yes | Alphanumeric | Geographic identifier (e.g. ward, road name, station ID, junction code). |
| `latitude` | Float | Yes | `15.0` to `23.5` (Maharashtra bounds) | WGS-84 decimal latitude. Must be measured or geocoded precisely. |
| `longitude` | Float | Yes | `72.0` to `82.5` (Maharashtra bounds) | WGS-84 decimal longitude. Must be measured or geocoded precisely. |
| `event_start_time` | String | Yes | ISO 8601 (`YYYY-MM-DDTHH:MM:SS+HH:MM`) | Onset timestamp. Timezone offset (e.g. `+05:30` for IST) is mandatory. |
| `event_end_time` | String / Null | No | ISO 8601 or empty | Recession timestamp when water drained. Leave empty if unrecorded or ongoing. |
| `waterlogging_observed` | Integer | Yes | `1` or `0` | **1**: Waterlogging occurred. <br>**0**: **Verified negative control observation** (an inspector actively confirmed dry conditions). <br>**CRITICAL RULE**: NEVER set to 0 merely because no complaint was logged. Non-reporting is not absence of waterlogging. |
| `severity_level` | String | No | `None`, `Low`, `Moderate`, `Severe`, `Critical`, `Unknown` | Physical disruption tier: <br>- `None`: Verified dry control.<br>- `Low`: Minor curb pooling, depth $<15\text{ cm}$.<br>- `Moderate`: Lane reduction, depth $15-30\text{ cm}$.<br>- `Severe`: Stalled vehicles, underpass closure, depth $30-60\text{ cm}$.<br>- `Critical`: Complete gridlock, structural inundation, depth $>60\text{ cm}$.<br>- `Unknown`: Waterlogging observed but depth unmeasured. |
| `water_depth_cm` | Float / Null | No | $\ge 0.0\text{ cm}$ or empty | Measured depth in centimeters. Leave empty if visual estimation only without gauge. |
| `evidence_type` | String | Yes | `Municipal_Log`, `Traffic_Police_Log`, `Physical_Inspection`, `CCTV_Feed`, `Citizen_Report_Verified`, `Automated_Sensor`, `Media_Verified`, `Field_Survey` | Empirical modality validating the observation. |
| `evidence_source` | String | Yes | Free text | Originating organization (e.g. Nagpur Municipal Corporation, Pune Traffic Police). |
| `verification_status` | String | Yes | `Verified_Official`, `Verified_Field`, `Unverified`, `Disputed`, `Rejected` | Verification tier. Only `Verified_Official` and `Verified_Field` are eligible for supervised training. |
| `image_path` | String / Null | No | Filepath or empty | Local or relative path to timestamped/geolocated photograph. |
| `annotator_id` | String | Yes | Alphanumeric | Operator or researcher ID responsible for logging the record. |
| `notes` | String / Null | No | Free text | Specific local context (e.g. underpass, broken drain, pump failure). |

---

## 2. Fundamental Scientific Rules for Ground Truth Collection

1. **No Negative Assumption from Absence of Records**:
   Municipal logging is often sparse. If a street has no recorded complaints, it does NOT mean it remained dry. Negative examples (`waterlogging_observed = 0`) must come from **active negative control observations** (such as regular patrol logs confirming dry streets during rain, or automated water-level sensor telemetry reading zero water height).

2. **Temporal Windowing**:
   `event_start_time` must be recorded to at least the nearest hour. This allows matching against the antecedent 1h, 3h, 6h, 24h, 48h, and 72h rainfall features preceding onset.

3. **Spatial Buffer Tolerance**:
   When matching events to rain stations, the maximum allowable distance is $25\text{ km}$ in plain topography, and $10\text{ km}$ in urban/hilly terrain. Events farther than $25\text{ km}$ from any active weather station will be flagged as unmatchable.
