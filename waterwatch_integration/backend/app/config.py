"""
WaterWatch AI Integration - Configuration Settings
Manages paths, environment variables, model locations, external API providers, and Google Maps API.
"""

import os
from pathlib import Path
from pydantic import BaseModel

INTEGRATION_ROOT = Path(__file__).resolve().parent.parent.parent
PROJECT_ROOT = INTEGRATION_ROOT.parent

DATA_DIR = INTEGRATION_ROOT / "data"
UPLOADS_DIR = DATA_DIR / "uploads"
DATA_DIR.mkdir(parents=True, exist_ok=True)
UPLOADS_DIR.mkdir(parents=True, exist_ok=True)

# Read-only paths to root project model artifacts
MODELS_DIR = PROJECT_ROOT / "models"
RAINFALL_MODEL_PATH = MODELS_DIR / "rainfall" / "synthetic_rainfall_model.joblib"
METEOROLOGICAL_BASELINE_PATH = MODELS_DIR / "rainfall" / "experimental_risk_baseline.joblib"
IMAGE_MODEL_PATH = MODELS_DIR / "image" / "best.pt"


class Settings(BaseModel):
    app_name: str = "WaterWatch AI — Nagpur Full-Stack Integration"
    version: str = "1.0.0"
    environment: str = os.getenv("ENVIRONMENT", "development")
    api_prefix: str = "/api/v1"
    host: str = os.getenv("INTEGRATION_HOST", "127.0.0.1")
    port: int = int(os.getenv("INTEGRATION_PORT", "8080"))
    database_url: str = os.getenv(
        "DATABASE_URL",
        f"sqlite:///{str(DATA_DIR / 'waterwatch_integration.db').replace('\\', '/')}"
    )
    admin_username: str = os.getenv("ADMIN_USERNAME", "admin")
    admin_password: str = os.getenv("ADMIN_PASSWORD", "admin123")
    admin_token: str = os.getenv("ADMIN_SECRET_KEY", "waterwatch_admin_secret_token_2026")
    osrm_base_url: str = os.getenv("OSRM_BASE_URL", "https://router.project-osrm.org")
    weather_api_url: str = os.getenv("WEATHER_API_URL", "https://api.open-meteo.com/v1/forecast")
    google_maps_api_key: str = os.getenv("GOOGLE_MAPS_API_KEY", "AIzaSyBFzKz2QQEzTO3h5youhcy67kjcpP9dmPM")
    allowed_origins: list = [
        "http://localhost:8080",
        "http://127.0.0.1:8080",
        "http://localhost:3000",
        "*"
    ]


settings = Settings()
