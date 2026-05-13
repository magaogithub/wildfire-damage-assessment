"""
Wildfire Damage Assessment Platform - FastAPI Backend
Production-ready with full async support, JWT auth, and microservices architecture
"""

from fastapi import FastAPI, Depends, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.gzip import GZIPMiddleware
from fastapi.middleware.trustedhost import TrustedHostMiddleware
from contextlib import asynccontextmanager
from datetime import datetime
import logging

from app.core.config import settings
from app.core.logging import setup_logging
from app.api.v1 import router as api_v1_router
from app.db.session import init_db

# Setup logging
setup_logging()
logger = logging.getLogger(__name__)

# ============================================================
# LIFESPAN EVENTS
# ============================================================

@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application startup and shutdown"""
    # Startup
    logger.info("🚀 Application starting...")
    try:
        await init_db()
        logger.info("✅ Database initialized")
    except Exception as e:
        logger.warning(f"⚠️  Database initialization skipped: {str(e)}")
    
    yield
    
    # Shutdown
    logger.info("🛑 Application shutting down...")

# ============================================================
# CREATE APP
# ============================================================

app = FastAPI(
    title="Wildfire Damage Assessment API",
    description="Advanced geospatial AI platform for fire damage analysis using Sentinel-2",
    version="1.0.0",
    docs_url="/api/docs",
    redoc_url="/api/redoc",
    openapi_url="/api/openapi.json",
    lifespan=lifespan
)

# ============================================================
# MIDDLEWARE STACK
# ============================================================

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Trusted Host
app.add_middleware(
    TrustedHostMiddleware,
    allowed_hosts=settings.ALLOWED_HOSTS
)

# GZIP compression
app.add_middleware(GZIPMiddleware, minimum_size=1000)

# ============================================================
# ROUTES
# ============================================================

@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "version": "1.0.0",
        "environment": settings.ENVIRONMENT,
        "timestamp": datetime.now().isoformat()
    }

@app.get("/api/v1/status")
async def status():
    """API status endpoint"""
    return {
        "status": "operational",
        "timestamp": datetime.now().isoformat(),
        "version": "1.0.0"
    }

# Include all API routes
app.include_router(api_v1_router, prefix="/api/v1")

# ============================================================
# EXCEPTION HANDLERS
# ============================================================

@app.exception_handler(HTTPException)
async def http_exception_handler(request, exc):
    """HTTP exception handler"""
    return {
        "detail": exc.detail,
        "status_code": exc.status_code,
        "timestamp": datetime.now().isoformat()
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "app.main:app",
        host="0.0.0.0",
        port=8000,
        reload=settings.ENVIRONMENT == "development",
        log_level="info"
    )
