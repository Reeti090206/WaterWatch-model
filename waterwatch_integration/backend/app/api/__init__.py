"""API routers package for WaterWatch Integration"""
from .dashboard import router as dashboard_router
from .incidents import router as incidents_router
from .reports import router as reports_router
from .rainfall import router as rainfall_router
from .detection import router as detection_router
from .routes import router as routes_router
from .hotspots import router as hotspots_router
