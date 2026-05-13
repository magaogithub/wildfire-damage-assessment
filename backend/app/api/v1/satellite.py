"""
Satellite Data API Endpoints
Handles Sentinel-2 image search and download
"""

from fastapi import APIRouter, Depends, HTTPException, status, BackgroundTasks
from sqlalchemy.orm import Session
from typing import List

from app.core.security import get_current_user
from app.db.session import get_db
from app.models.database import User, AreaOfInterest, SatelliteImage
from app.models.schemas import (
    SatelliteSearchRequest, SatelliteImageResponse
)

router = APIRouter(prefix="/satellite", tags=["Satellite Data"])

@router.post("/search", response_model=List[SatelliteImageResponse])
async def search_satellite_images(
    request: SatelliteSearchRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Search for Sentinel-2 images"""
    
    # Verify AOI belongs to user
    aoi = db.query(AreaOfInterest).filter(
        AreaOfInterest.id == request.area_id,
        AreaOfInterest.user_id == current_user.id
    ).first()
    
    if not aoi:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="AOI not found"
        )
    
    # Return mock satellite images for now
    # In production, integrate with SentinelHub API
    return []

@router.get("/images/{aoi_id}", response_model=List[SatelliteImageResponse])
async def list_satellite_images(
    aoi_id: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """List satellite images for AOI"""
    
    aoi = db.query(AreaOfInterest).filter(
        AreaOfInterest.id == aoi_id,
        AreaOfInterest.user_id == current_user.id
    ).first()
    
    if not aoi:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="AOI not found"
        )
    
    images = db.query(SatelliteImage).filter(
        SatelliteImage.area_id == aoi_id
    ).all()
    
    return images
