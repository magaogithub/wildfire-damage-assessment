"""
Map Management API Endpoints
Handles AOI (Area of Interest) CRUD operations
"""

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List

from app.core.security import get_current_user
from app.db.session import get_db
from app.models.database import User, AreaOfInterest
from app.models.schemas import AOICreateRequest, AOIResponse

router = APIRouter(prefix="/map", tags=["Map Management"])

@router.get("/aoi", response_model=List[AOIResponse])
async def list_aoi(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
    skip: int = 0,
    limit: int = 50
):
    """List all AOIs for current user"""
    
    aois = db.query(AreaOfInterest).filter(
        AreaOfInterest.user_id == current_user.id
    ).offset(skip).limit(limit).all()
    
    return aois

@router.post("/aoi", response_model=AOIResponse, status_code=status.HTTP_201_CREATED)
async def create_aoi(
    request: AOICreateRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Create a new Area of Interest"""
    
    aoi = AreaOfInterest(
        user_id=current_user.id,
        name=request.name,
        description=request.description,
        geometry=f"SRID=4326;{request.geometry}",  # GeoJSON to WKT conversion
        is_public=request.is_public,
        metadata=request.metadata
    )
    
    db.add(aoi)
    db.commit()
    db.refresh(aoi)
    
    return aoi

@router.get("/aoi/{aoi_id}", response_model=AOIResponse)
async def get_aoi(
    aoi_id: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get AOI by ID"""
    
    aoi = db.query(AreaOfInterest).filter(
        AreaOfInterest.id == aoi_id,
        AreaOfInterest.user_id == current_user.id
    ).first()
    
    if not aoi:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="AOI not found"
        )
    
    return aoi

@router.put("/aoi/{aoi_id}", response_model=AOIResponse)
async def update_aoi(
    aoi_id: str,
    request: AOICreateRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Update AOI"""
    
    aoi = db.query(AreaOfInterest).filter(
        AreaOfInterest.id == aoi_id,
        AreaOfInterest.user_id == current_user.id
    ).first()
    
    if not aoi:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="AOI not found"
        )
    
    aoi.name = request.name
    aoi.description = request.description
    aoi.is_public = request.is_public
    aoi.metadata = request.metadata
    
    db.commit()
    db.refresh(aoi)
    
    return aoi

@router.delete("/aoi/{aoi_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_aoi(
    aoi_id: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Delete AOI"""
    
    aoi = db.query(AreaOfInterest).filter(
        AreaOfInterest.id == aoi_id,
        AreaOfInterest.user_id == current_user.id
    ).first()
    
    if not aoi:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="AOI not found"
        )
    
    db.delete(aoi)
    db.commit()
    
    return None
