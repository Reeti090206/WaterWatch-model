"""
WaterWatch AI Integration - Main FastAPI Application
Serves RESTful APIs and the frontend interactive web dashboard.
"""

from pathlib import Path
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse

from waterwatch_integration.backend.app.config import settings, UPLOADS_DIR, INTEGRATION_ROOT
from waterwatch_integration.backend.app.database.models import init_db
from waterwatch_integration.backend.app.api.dashboard import router as dashboard_router
from waterwatch_integration.backend.app.api.incidents import router as incidents_router
from waterwatch_integration.backend.app.api.reports import router as reports_router
from waterwatch_integration.backend.app.api.rainfall import router as rainfall_router
from waterwatch_integration.backend.app.api.detection import router as detection_router
from waterwatch_integration.backend.app.api.routes import router as routes_router
from waterwatch_integration.backend.app.api.hotspots import router as hotspots_router

from contextlib import asynccontextmanager

@asynccontextmanager
async def lifespan(app: FastAPI):
    init_db()
    yield

# Initialize FastAPI app
app = FastAPI(
    title=settings.app_name,
    version=settings.version,
    description=(
        "Real-Time & Predictive Waterlogging Monitoring and Intelligent Route Recommendation System for Nagpur. "
        "Integrates ML predictions, computer vision detection, spatial hazard assessment, and civic reporting."
    ),
    docs_url="/docs",
    redoc_url="/redoc",
    lifespan=lifespan
)

# CORS Middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.allowed_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Register API Routers under /api/v1
app.include_router(dashboard_router, prefix=settings.api_prefix)
app.include_router(incidents_router, prefix=settings.api_prefix)
app.include_router(reports_router, prefix=settings.api_prefix)
app.include_router(rainfall_router, prefix=settings.api_prefix)
app.include_router(detection_router, prefix=settings.api_prefix)
app.include_router(routes_router, prefix=settings.api_prefix)
app.include_router(hotspots_router, prefix=settings.api_prefix)

# Mount Uploads directory for photo previews
UPLOADS_DIR.mkdir(parents=True, exist_ok=True)
app.mount("/api/v1/uploads", StaticFiles(directory=str(UPLOADS_DIR)), name="uploads")

# Frontend directory
FRONTEND_DIR = INTEGRATION_ROOT / "frontend"
if FRONTEND_DIR.exists():
    app.mount("/static", StaticFiles(directory=str(FRONTEND_DIR)), name="static")

    @app.get("/")
    def serve_frontend_index():
        index_file = FRONTEND_DIR / "index.html"
        if index_file.exists():
            return FileResponse(str(index_file))
        return {"message": "WaterWatch AI Integration Backend is running. Frontend index.html not found."}


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "waterwatch_integration.backend.app.main:app",
        host=settings.host,
        port=settings.port,
        reload=True
    )
