# WaterWatch AI — Full-Stack Integration

**Project Title:** Real-Time and Predictive Waterlogging Monitoring and Intelligent Route Recommendation System for Nagpur  
**Branch:** `fullstack`  
**Frontend Architecture:** Next.js 14 (App Router) + TypeScript + Google Maps JavaScript API + Glassmorphic Design  
**Backend Architecture:** FastAPI + SQLAlchemy (SQLite) + Scikit-Learn Pipeline + Ultralytics YOLOv11 + Live Open-Meteo Weather  

---

## 1. Strict File Preservation & Isolation Guarantee

This entire full-stack integration resides strictly within the isolated `waterwatch_integration/` directory:

- **Zero modifications** to existing root project files outside `waterwatch_integration/` (`scripts/`, `data/`, `ml/`, `models/`, `reports/`, etc.).
- **Read-only access** to pre-trained ML model artifacts (`models/rainfall/synthetic_rainfall_model.joblib` and `models/image/best.pt`).
- **Completely isolated database and uploads** stored exclusively within `waterwatch_integration/data/` and `waterwatch_integration/data/uploads/`.
- **Model Truthfulness & Provenance:** The production municipal rainfall model remains documented as `BLOCKED_ON_VERIFIED_DATA`, while the synthetic model is labeled as `SYNTHETIC_EXPERIMENTAL` throughout all UI elements, API responses, and database audits.

---

## 2. Directory Structure

```
waterwatch_integration/
├── backend/
│   ├── app/
│   │   ├── adapters/
│   │   │   ├── rainfall_adapter.py      # Read-only adapter for synthetic rainfall model
│   │   │   ├── image_adapter.py         # Read-only adapter for YOLOv11 detector
│   │   │   └── weather_adapter.py       # Live Open-Meteo weather client + offline fallback
│   │   ├── api/
│   │   │   ├── dashboard.py             # System status, stats, and Google Maps config
│   │   │   ├── incidents.py             # Active waterlogging incidents & closures
│   │   │   ├── reports.py               # Citizen reporting & authority review workflow
│   │   │   ├── rainfall.py              # Rainfall risk prediction & history
│   │   │   ├── detection.py             # Computer vision waterlogging detection
│   │   │   ├── routes.py                # Intelligent route recommendation
│   │   │   └── hotspots.py              # Historical hotspots & municipal analytics
│   │   ├── database/
│   │   │   ├── connection.py            # SQLite engine & session factory
│   │   │   └── models.py                # Incidents, Reports, Hotspots, Closures, Audits
│   │   ├── schemas/                     # Pydantic V2 request/response models
│   │   ├── services/
│   │   │   ├── risk_scoring.py          # Spatial buffer & multi-factor risk computation
│   │   │   ├── routing_service.py       # Multi-criterion routing (Fastest, Safest, Balanced)
│   │   │   └── hotspot_service.py       # Nagpur hotspots & recurring flood analytics
│   │   ├── config.py                    # Environment settings, model paths & Google Maps key
│   │   └── main.py                      # FastAPI app entry with CORS & API routing
│   └── tests/
│       └── test_integration_api.py      # Automated integration & root-preservation test suite (11/11 passing)
├── frontend/                            # Next.js 14 + TypeScript Frontend
│   ├── src/
│   │   ├── app/
│   │   │   ├── globals.css              # Custom glassmorphic dark theme tokens
│   │   │   ├── layout.tsx               # Next.js root layout with Inter typography
│   │   │   └── page.tsx                 # Main application dashboard orchestrator
│   │   ├── components/
│   │   │   ├── GoogleMapComponent.tsx   # Google Maps JS API (Nagpur dark map + layers + polyline)
│   │   │   ├── Navbar.tsx               # Header with live weather radar ticker
│   │   │   ├── DashboardSummaryView.tsx # High-impact operational KPI cards & incident feed
│   │   │   ├── RouteRecommendationView.tsx # Multi-criterion safe route planner
│   │   │   ├── RainfallPredictionView.tsx # Rainfall ML risk inference gauge
│   │   │   ├── ImageDetectionView.tsx   # YOLOv11 optical flood detector & canvas visualizer
│   │   │   ├── CitizenReportView.tsx    # Civic reporting form & moderation feed
│   │   │   ├── AdminReviewModal.tsx     # Municipal verification & incident elevation modal
│   │   │   ├── HotspotsAnalyticsView.tsx# Nagpur RUB underpasses & chronic flood causes
│   │   │   └── ModelStatusView.tsx      # Transparent ML readiness & data blocker report
│   │   ├── services/
│   │   │   └── api.ts                   # Strongly typed API client communicating with /api/v1
│   │   └── types/
│   │       └── index.ts                 # TypeScript type interfaces
│   ├── next.config.mjs                  # Next.js config with reverse-proxy rewrites to backend
│   ├── package.json                     # Dependencies: next, react, typescript, lucide-react
│   └── tsconfig.json                    # TypeScript compiler configuration
├── data/                                # Isolated SQLite database and seed storage
├── run_integration.py                   # Single-command launcher for backend
└── README.md                            # Complete integration documentation
```

---

## 3. Quickstart & Execution

### Option A: Launch Both Backend and Next.js Frontend

**Step 1: Start FastAPI Backend** (Terminal 1)
```bash
python waterwatch_integration/run_integration.py
```
- Backend runs on: `http://127.0.0.1:8080`
- Swagger API Docs: `http://127.0.0.1:8080/docs`

**Step 2: Start Next.js Frontend** (Terminal 2)
```bash
cd waterwatch_integration/frontend
npm run dev
```
- Interactive Next.js Dashboard: `http://localhost:3000`

### Option B: Next.js Production Build
```bash
cd waterwatch_integration/frontend
npm run build
npm start
```

---

## 4. Google Maps API Integration

The frontend utilizes the provided Google Maps API Key (`AIzaSyBFzKz2QQEzTO3h5youhcy67kjcpP9dmPM`):
- **Map View:** Centered on Nagpur (`21.1458° N, 79.0882° E`) with a curated dark cartographic theme.
- **Layer Controls:** Toggle markers for:
  - 🔴 Active Incidents (color-coded by severity: Low, Moderate, High, Critical)
  - 🟣 Chronic Hotspots (Mor Bhavan, Sitabuldi, Narendra Nagar RUB)
  - 🚫 Active Road Closures
  - 🟡 Citizen Reports
- **Interactive Route Polylines:** When calculating safe routes, the polyline is rendered dynamically on the Google Map in green (safest) / orange / red based on the calculated multi-factor flood risk score.

---

## 5. Automated Verification

Run the integration test suite:
```bash
pytest waterwatch_integration/backend/tests/test_integration_api.py -v
```
All 11 tests pass:
1. `test_root_files_untouched`: Asserts 0 modified or deleted files outside `waterwatch_integration/`.
2. `test_health_endpoint`: Asserts database connectivity and model status.
3. `test_models_status_provenance`: Asserts `SYNTHETIC_EXPERIMENTAL` labeling and `BLOCKED ON DATA` status.
4. `test_maps_config_endpoint`: Asserts Google Maps API key propagation.
5. `test_dashboard_summary`: Asserts operational KPI calculation.
6. `test_hotspots_list`: Asserts seeded Nagpur underpass hotspots.
7. `test_road_closures_list`: Asserts road closures API.
8. `test_rainfall_prediction_flow`: Asserts end-to-end ML model inference.
9. `test_citizen_report_submission_and_review`: Asserts report creation and authority moderation flow.
10. `test_route_recommendation`: Asserts multi-criterion routing with flood hazard scoring.
11. `test_image_detection_endpoint`: Asserts optical YOLOv11 inference.
