"""
WaterWatch AI - Full-Stack Integration Runner
Launches FastAPI backend serving both API routes and frontend single-page application.
Ensures zero modification to existing project files outside waterwatch_integration/.
"""

import sys
import os
from pathlib import Path

# Add project root to sys.path so waterwatch_integration can be imported cleanly
ROOT_DIR = Path(__file__).resolve().parent.parent
if str(ROOT_DIR) not in sys.path:
    sys.path.insert(0, str(ROOT_DIR))

# Ensure site-packages on Windows root drive installation is accessible
for sp in [Path("D:/Lib/site-packages"), Path(sys.prefix) / "Lib" / "site-packages"]:
    if sp.exists() and str(sp) not in sys.path:
        sys.path.append(str(sp))

import uvicorn
from waterwatch_integration.backend.app.config import settings, RAINFALL_MODEL_PATH, IMAGE_MODEL_PATH, DATA_DIR

def main():
    print("=" * 70)
    print(" WATERWATCH AI - FULL-STACK INTEGRATION RUNNER")
    print(f" Environment Mode   : {settings.environment}")
    print(f" Host & Port        : {settings.host}:{settings.port}")
    print(f" Rainfall Model Path: {RAINFALL_MODEL_PATH}")
    print(f" Image Model Path   : {IMAGE_MODEL_PATH}")
    print(f" Database Dir       : {DATA_DIR}")
    print(f" Google Maps Key    : {settings.google_maps_api_key[:10]}... (Configured)")
    print("=" * 70)
    print(f" Access Web Dashboard at: http://{settings.host}:{settings.port}")
    print(f" Access Swagger Docs at:  http://{settings.host}:{settings.port}/docs")
    print(" Press Ctrl+C to stop the server.")
    print("=" * 70)

    uvicorn.run(
        "waterwatch_integration.backend.app.main:app",
        host=settings.host,
        port=settings.port,
        reload=False,
        log_level="info",
    )

if __name__ == "__main__":
    main()
