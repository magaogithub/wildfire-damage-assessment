"""
Pydantic Schemas for API Request/Response Validation
"""

from pydantic import BaseModel, EmailStr, Field
from typing import Optional, List, Dict, Any
from datetime import datetime
from enum import Enum
import uuid

# ============================================================
# ENUMS
# ============================================================

class UserRole(str, Enum):
    ADMIN = "admin"
    ANALYST = "analyst"
    OBSERVER = "observer"

class DamageClass(str, Enum):
    INTACT = "intact"
    DAMAGED = "damaged"
    DESTROYED = "destroyed"

class BurnSeverity(str, Enum):
    ENHANCED_REGENERATION = "enhanced_regeneration"
    UNBURNED = "unburned"
    LOW = "low"
    MODERATE_LOW = "moderate_low"
    MODERATE_HIGH = "moderate_high"
    HIGH = "high"

# ============================================================
# AUTH SCHEMAS
# ============================================================

class RegisterRequest(BaseModel):
    email: EmailStr
    username: str = Field(..., min_length=3, max_length=100)
    password: str = Field(..., min_length=8)
    full_name: str
    organization: Optional[str] = None

class LoginRequest(BaseModel):
    email: EmailStr
    password: str

class TokenResponse(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str = "bearer"
    expires_in: int

class UserResponse(BaseModel):
    id: uuid.UUID
    email: str
    username: str
    full_name: str
    role: UserRole
    organization: Optional[str]
    avatar_url: Optional[str]
    is_active: bool
    is_verified: bool
    created_at: datetime
    last_login: Optional[datetime]
    
    class Config:
        from_attributes = True

# ============================================================
# MAP/AOI SCHEMAS
# ============================================================

class GeometryPoint(BaseModel):
    type: str = "Point"
    coordinates: List[float]  # [lon, lat]

class GeometryPolygon(BaseModel):
    type: str = "Polygon"
    coordinates: List[List[List[float]]]  # [[[lon, lat], ...]]

class AOICreateRequest(BaseModel):
    name: str = Field(..., min_length=3, max_length=255)
    description: Optional[str] = None
    geometry: Dict[str, Any]  # GeoJSON geometry
    is_public: bool = False
    metadata: Optional[Dict[str, Any]] = None

class AOIResponse(BaseModel):
    id: uuid.UUID
    name: str
    description: Optional[str]
    area_sqm: float
    is_public: bool
    created_at: datetime
    updated_at: datetime
    metadata: Optional[Dict[str, Any]]
    
    class Config:
        from_attributes = True

# ============================================================
# SATELLITE SCHEMAS
# ============================================================

class SatelliteSearchRequest(BaseModel):
    area_id: uuid.UUID
    start_date: datetime
    end_date: datetime
    max_cloud_cover: float = Field(default=30.0, ge=0, le=100)
    limit: int = Field(default=10, ge=1, le=100)

class SatelliteImageResponse(BaseModel):
    id: uuid.UUID
    area_id: uuid.UUID
    acquisition_date: datetime
    cloud_cover: float
    sensor: str
    s3_path: str
    s3_thumbnail: Optional[str]
    processing_status: str
    created_at: datetime
    
    class Config:
        from_attributes = True

# ============================================================
# ANALYSIS SCHEMAS
# ============================================================

class AnalysisCreateRequest(BaseModel):
    area_id: uuid.UUID
    date_before: datetime = Field(..., description="Date before fire")
    date_after: datetime = Field(..., description="Date after fire")
    cloud_cover_threshold: float = Field(default=30.0, ge=0, le=100)

class AnalysisStatistics(BaseModel):
    mean_nbr: float
    mean_dnbr: float
    mean_ndvi: float
    unburned_area_sqm: float
    low_severity_sqm: float
    moderate_severity_sqm: float
    high_severity_sqm: float
    high_severity_pct: float

class AnalysisResultsResponse(BaseModel):
    id: uuid.UUID
    area_id: uuid.UUID
    statistics: Dict[str, Any]
    analysis_timestamp: datetime
    processing_time_seconds: float
    
    class Config:
        from_attributes = True

class TaskStatusResponse(BaseModel):
    task_id: str
    status: str  # pending, processing, completed, failed
    result: Optional[Dict[str, Any]]
    error: Optional[str]

# ============================================================
# BUILDING DETECTION SCHEMAS
# ============================================================

class DetectedBuildingResponse(BaseModel):
    id: uuid.UUID
    confidence_score: float
    damage_class: DamageClass
    damage_confidence: float
    building_area_sqm: float
    ndvi_change: float
    metadata: Optional[Dict[str, Any]]
    detected_at: datetime
    
    class Config:
        from_attributes = True

class DamageStatisticsResponse(BaseModel):
    total_buildings_detected: int
    buildings_intact: int
    buildings_damaged: int
    buildings_destroyed: int
    total_building_area_sqm: float
    affected_building_area_sqm: float
    destruction_rate: float
    
    class Config:
        from_attributes = True

# ============================================================
# REPORT SCHEMAS
# ============================================================

class ReportGenerateRequest(BaseModel):
    analysis_id: uuid.UUID
    report_type: str = Field(default="pdf", regex="^(pdf|html|json)$")
    title: Optional[str] = None
    include_maps: bool = True
    include_statistics: bool = True
    include_ai_results: bool = True

class ReportResponse(BaseModel):
    id: uuid.UUID
    title: str
    report_type: str
    s3_path: str
    generated_at: datetime
    file_size_mb: float
    
    class Config:
        from_attributes = True

# ============================================================
# EXPORT SCHEMAS
# ============================================================

class ExportRequest(BaseModel):
    analysis_id: uuid.UUID
    format: str = Field(..., regex="^(geotiff|png|geojson|csv)$")
    include_metadata: bool = True

class ExportResponse(BaseModel):
    export_id: uuid.UUID
    format: str
    s3_path: str
    file_size_mb: float
    download_url: str
