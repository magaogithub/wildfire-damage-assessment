"""API v1 routes"""

from fastapi import APIRouter
from app.api.v1 import auth, map_routes, satellite, analysis

router = APIRouter()

# Include all route modules
router.include_router(auth.router)
router.include_router(map_routes.router)
router.include_router(satellite.router)
router.include_router(analysis.router)
