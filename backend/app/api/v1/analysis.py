"""
Analysis API Endpoints
Handles fire damage analysis workflows
"""

from fastapi import APIRouter, Depends, HTTPException, status, BackgroundTasks
from sqlalchemy.orm import Session

from app.core.security import get_current_user
from app.db.session import get_db
from app.models.database import User, AreaOfInterest, RasterAnalysis
from app.models.schemas import (
    AnalysisCreateRequest, AnalysisResultsResponse, TaskStatusResponse
)

router = APIRouter(prefix="/analysis", tags=["Analysis"])

@router.post("/create", response_model=TaskStatusResponse)
async def create_analysis(
    request: AnalysisCreateRequest,
    background_tasks: BackgroundTasks,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Create a new fire damage analysis"""
    
    # Verify AOI exists
    aoi = db.query(AreaOfInterest).filter(
        AreaOfInterest.id == request.area_id,
        AreaOfInterest.user_id == current_user.id
    ).first()
    
    if not aoi:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="AOI not found"
        )
    
    # For now, return mock response
    # In production, queue Celery task
    return TaskStatusResponse(
        task_id="mock_task_id",
        status="pending",
        result=None,
        error=None
    )

@router.get("/results/{analysis_id}", response_model=AnalysisResultsResponse)
async def get_analysis_results(
    analysis_id: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get analysis results"""
    
    analysis = db.query(RasterAnalysis).filter(
        RasterAnalysis.id == analysis_id
    ).first()
    
    if not analysis:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Analysis not found"
        )
    
    return analysis
