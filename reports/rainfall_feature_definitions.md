# WaterWatch AI — Rainfall Feature Definitions & Hydrological Formulation

**Document Version**: 1.1  
**Scope**: Maharashtra State Observation Network (Daily Manual & Hourly Telemetry)  
**Standard**: India Meteorological Department (IMD) Precipitation Thresholds & Antecedent Hydrology  

---

## 1. Feature Specifications Matrix

| Feature Name | Granularity | Physical Unit | Formulation / Definition | Temporal Guard / Leakage Prevention | Missing Value Policy |
| :--- | :--- | :--- | :--- | :--- | :--- |
| `rainfall_mm` / `rainfall_24h_mm` | Daily | mm | 24-hour total precipitation measured at 08:30 IST. | Represents preceding 24 hours ending at observation timestamp. | Stored as recorded; missing dates not imputed. |
| `rainfall_prev1_day_mm` | Daily | mm | 24-hour precipitation on day $t-1$ ($\text{Lag}_1$). | Strictly backward shift by 1 day (`shift(1)`). | `NaN` if previous day is missing or observation gap $> 1$ day. |
| `rainfall_prev2_day_mm` | Daily | mm | 24-hour precipitation on day $t-2$ ($\text{Lag}_2$). | Strictly backward shift by 2 days (`shift(2)`). | `NaN` if day $t-2$ is missing or observation gap $> 2$ days. |
| `rainfall_2day_total_mm` / `rainfall_48h_mm` | Daily | mm | $R_t + R_{t-1}$ over consecutive 48-hour window. | Strictly backward accumulation. | `NaN` if $R_{t-1}$ is missing. |
| `rainfall_3day_total_mm` / `rainfall_72h_mm` | Daily | mm | $R_t + R_{t-1} + R_{t-2}$ over consecutive 72-hour window. | Strictly backward accumulation. | `NaN` if any component day is missing. |
| `api_7day` | Daily | mm | Antecedent Precipitation Index: $\text{API}_t = 0.85 \times (\text{API}_{t-1} + R_{t-1})$. | Computed recursively using only past days ($< t$). | Decay coefficient $\lambda = 0.85$ per day. |
| `rainfall_trend_ratio` | Daily | Unitless $[0, 1]$ | $R_t / \text{rainfall\_3day\_total\_mm}$. Measures acute concentration. | Backward ratio. | Set to 1.0 if 3-day total is 0.0. |
| `imd_category` | Daily | Categorical | IMD rainfall intensity classification (Very Light to Extremely Heavy). | Stratified on current 24-hour rainfall. | Categorized as "No Rain" if $\le 0.0$ mm. |
| `is_monsoon` | Daily/Hourly | Binary $\{0, 1\}$ | Flag indicating Southwest Monsoon season (June, July, August, September). | Derived strictly from calendar month. | Deterministic. |
| `rainfall_1h_mm` | Hourly | mm | Acute precipitation recorded in 1-hour telemetry slot. | Preceding 60 minutes ending at timestamp. | `NaN` if unmeasured (NEVER zero). |
| `rolling_3h_mm` | Hourly | mm | Rolling 3-hour cumulative precipitation. | Time-based rolling window with `closed='right'`. | Requires $\ge 2$ valid hourly readings in window; else `NaN`. |
| `rolling_6h_mm` | Hourly | mm | Rolling 6-hour cumulative precipitation. | Time-based rolling window with `closed='right'`. | Requires $\ge 4$ valid hourly readings in window; else `NaN`. |
| `rolling_24h_mm` | Hourly | mm | Rolling 24-hour cumulative precipitation. | Time-based rolling window with `closed='right'`. | Requires $\ge 16$ valid hourly readings in window; else `NaN`. |
| `rolling_72h_mm` | Hourly | mm | Rolling 72-hour cumulative precipitation. | Time-based rolling window with `closed='right'`. | Requires $\ge 48$ valid hourly readings in window; else `NaN`. |

---

## 2. Temporal Resolution Boundaries

1. **Daily Manual Records (`rainfall_manual_daily_maharashtra_sw_mh_2021_2025.csv`)**:
   - Frequency: Once daily at 08:30 IST.
   - Sub-daily windows (1h, 3h, 6h) **cannot be computed** without falsifying temporal granularity. Any model requiring hourly features must be trained on hourly telemetry sources.

2. **Hourly Telemetry Records (`rainfall_tel_hr_cwc_mh_2021_2025.csv`)**:
   - Frequency: Hourly.
   - High missingness (91.53% across CWC network).
   - **Strict Non-Zero Rule**: In adherence to scientific integrity, unrecorded hours are treated as `NaN` and never filled as `0.0`. Rolling windows require minimum valid observation thresholds.

---

## 3. India Meteorological Department (IMD) Classification Standard

Precipitation intensity categories are calibrated against IMD criteria:
- **No Rain**: $0.0 \text{ mm}$
- **Very Light Rain**: $0.1 - 2.4 \text{ mm}$
- **Light Rain**: $2.5 - 15.5 \text{ mm}$
- **Moderate Rain**: $15.6 - 64.4 \text{ mm}$
- **Heavy Rain**: $64.5 - 115.5 \text{ mm}$ (Threshold for significant urban surface runoff)
- **Very Heavy Rain**: $115.6 - 204.4 \text{ mm}$ (Severe urban waterlogging hazard)
- **Extremely Heavy Rain**: $> 204.4 \text{ mm}$ (Flash flooding / cloudburst condition)
