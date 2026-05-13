"""
SQLAlchemy Database Models
Defines all database tables for the application
"""

from sqlalchemy import Column, String, Integer, Float, Boolean, DateTime, Text, JSONB, ForeignKey, Index, Table
from sqlalchemy.dialects.postgresql import UUID, ARRAY
from sqlalchemy.orm import relationship
from geoalchemy2 import Geometry, Raster
from datetime import datetime
import uuid

from app.db.session import Base

# ============================================================
# USERS & AUTHENTICATION
# ============================================================

class User(Base):
    __tablename__ = "users"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    email = Column(String(255), unique=True, nullable=False, index=True)
    username = Column(String(100), unique=True, nullable=False, index=True)
    password_hash = Column(String(255), nullable=False)
    full_name = Column(String(255))
    role = Column(String(50), default="observer")  # admin, analyst, observer
    organization = Column(String(255))
    avatar_url = Column(Text)
    is_active = Column(Boolean, default=True, index=True)
    is_verified = Column(Boolean, default=False)
    created_at = Column(DateTime, default=datetime.utcnow, index=True)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    last_login = Column(DateTime)
    
    # Relationships
    areas_of_interest = relationship("AreaOfInterest", back_populates="user", cascade="all, delete-orphan")
    reports = relationship("GeneratedReport", back_populates="user", cascade="all, delete-orphan")
    notifications = relationship("UserNotification", back_populates="user", cascade="all, delete-orphan")

class RefreshToken(Base):
    __tablename__ = "refresh_tokens"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    token = Column(String(500), unique=True, nullable=False)
    expires_at = Column(DateTime, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    revoked = Column(Boolean, default=False)

# ============================================================
# AREAS OF INTEREST (AOI)
# ============================================================

class AreaOfInterest(Base):
    __tablename__ = "areas_of_interest"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    name = Column(String(255), nullable=False)
    description = Column(Text)
    geometry = Column(Geometry("Polygon", srid=4326), nullable=False)
    area_sqm = Column(Float)
    created_at = Column(DateTime, default=datetime.utcnow, index=True)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    is_public = Column(Boolean, default=False)
    metadata = Column(JSONB)
    
    # Relationships
    user = relationship("User", back_populates="areas_of_interest")
    satellite_images = relationship("SatelliteImage", back_populates="area", cascade="all, delete-orphan")
    analysis_history = relationship("AreaAnalysisHistory", back_populates="area", cascade="all, delete-orphan")
    raster_analyses = relationship("RasterAnalysis", back_populates="area", cascade="all, delete-orphan")
    detected_buildings = relationship("DetectedBuilding", back_populates="area", cascade="all, delete-orphan")
    lulc_classifications = relationship("LULCClassification", back_populates="area", cascade="all, delete-orphan")
    
    # Indexes
    __table_args__ = (
        Index('idx_aoi_user', 'user_id', 'created_at'),
    )

class AreaAnalysisHistory(Base):
    __tablename__ = "area_analysis_history"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    area_id = Column(UUID(as_uuid=True), ForeignKey("areas_of_interest.id", ondelete="CASCADE"), nullable=False)
    analysis_date = Column(DateTime)
    total_burned_area_sqm = Column(Float)
    severity_distribution = Column(JSONB)  # {low: %, moderate: %, high: %}
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # Relationships
    area = relationship("AreaOfInterest", back_populates="analysis_history")

# ============================================================
# SATELLITE DATA & IMAGERY
# ============================================================

class SatelliteImage(Base):
    __tablename__ = "satellite_images"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    area_id = Column(UUID(as_uuid=True), ForeignKey("areas_of_interest.id", ondelete="CASCADE"), nullable=False)
    acquisition_date = Column(DateTime, nullable=False)
    cloud_cover = Column(Float)
    sensor = Column(String(50))  # S2A, S2B
    tile_id = Column(String(50))
    s3_path = Column(Text, nullable=False)
    s3_thumbnail = Column(Text)
    band_b2 = Column(Text)  # Blue 490nm
    band_b3 = Column(Text)  # Green 560nm
    band_b4 = Column(Text)  # Red 665nm
    band_b8 = Column(Text)  # NIR 842nm
    band_b11 = Column(Text)  # SWIR 1610nm
    band_b12 = Column(Text)  # SWIR 2190nm
    processing_status = Column(String(50), default="pending")  # pending, processing, completed, failed
    processed_at = Column(DateTime)
    metadata = Column(JSONB)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # Relationships
    area = relationship("AreaOfInterest", back_populates="satellite_images")
    
    # Indexes
    __table_args__ = (
        Index('idx_satellite_area', 'area_id', 'acquisition_date'),
        Index('idx_satellite_status', 'processing_status'),
    )

# ============================================================
# RASTER ANALYSIS RESULTS
# ============================================================

class RasterAnalysis(Base):
    __tablename__ = "raster_analysis"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    area_id = Column(UUID(as_uuid=True), ForeignKey("areas_of_interest.id"), nullable=False)
    pre_fire_image_id = Column(UUID(as_uuid=True), ForeignKey("satellite_images.id"))
    post_fire_image_id = Column(UUID(as_uuid=True), ForeignKey("satellite_images.id"), nullable=False)
    
    # Indices
    mean_nbr = Column(Float)
    mean_dnbr = Column(Float)
    mean_ndvi = Column(Float)
    statistics = Column(JSONB)
    
    # Severity distribution
    unburned_area_sqm = Column(Float)
    low_severity_sqm = Column(Float)
    moderate_severity_sqm = Column(Float)
    high_severity_sqm = Column(Float)
    
    analysis_timestamp = Column(DateTime, default=datetime.utcnow)
    processing_time_seconds = Column(Float)
    
    # Relationships
    area = relationship("AreaOfInterest", back_populates="raster_analyses")
    detected_buildings = relationship("DetectedBuilding", back_populates="analysis")
    damage_statistics = relationship("DamageStatistics", back_populates="analysis", uselist=False)
    lulc_classifications = relationship("LULCClassification", back_populates="analysis")
    reports = relationship("GeneratedReport", back_populates="analysis")

# ============================================================
# BUILDING DETECTION & DAMAGE ASSESSMENT
# ============================================================

class DetectedBuilding(Base):
    __tablename__ = "detected_buildings"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    area_id = Column(UUID(as_uuid=True), ForeignKey("areas_of_interest.id"), nullable=False)
    analysis_id = Column(UUID(as_uuid=True), ForeignKey("raster_analysis.id"), nullable=False)
    
    geometry = Column(Geometry("Point", srid=4326))
    building_polygon = Column(Geometry("Polygon", srid=4326))
    
    confidence_score = Column(Float)  # 0-1 YOLOv8 confidence
    damage_class = Column(String(50))  # intact, damaged, destroyed
    damage_confidence = Column(Float)
    
    building_area_sqm = Column(Float)
    pre_fire_ndvi = Column(Float)
    post_fire_ndvi = Column(Float)
    ndvi_change = Column(Float)
    
    metadata = Column(JSONB)
    detected_at = Column(DateTime, default=datetime.utcnow)
    
    # Relationships
    area = relationship("AreaOfInterest", back_populates="detected_buildings")
    analysis = relationship("RasterAnalysis", back_populates="detected_buildings")

class DamageStatistics(Base):
    __tablename__ = "damage_statistics"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    area_id = Column(UUID(as_uuid=True), ForeignKey("areas_of_interest.id"), nullable=False)
    analysis_id = Column(UUID(as_uuid=True), ForeignKey("raster_analysis.id"), nullable=False, unique=True)
    
    total_buildings_detected = Column(Integer)
    buildings_intact = Column(Integer)
    buildings_damaged = Column(Integer)
    buildings_destroyed = Column(Integer)
    
    total_building_area_sqm = Column(Float)
    affected_building_area_sqm = Column(Float)
    destruction_rate = Column(Float)
    
    statistical_summary = Column(JSONB)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # Relationships
    analysis = relationship("RasterAnalysis", back_populates="damage_statistics")

# ============================================================
# LAND USE / LAND COVER
# ============================================================

class LULCClassification(Base):
    __tablename__ = "lulc_classification"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    area_id = Column(UUID(as_uuid=True), ForeignKey("areas_of_interest.id"), nullable=False)
    analysis_id = Column(UUID(as_uuid=True), ForeignKey("raster_analysis.id"), nullable=False)
    
    # Areas by class
    forest_sqm = Column(Float)
    agriculture_sqm = Column(Float)
    urban_sqm = Column(Float)
    water_sqm = Column(Float)
    grassland_sqm = Column(Float)
    
    # Impact analysis
    forest_burned_sqm = Column(Float)
    agriculture_affected_sqm = Column(Float)
    urban_affected_sqm = Column(Float)
    
    lulc_summary = Column(JSONB)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # Relationships
    area = relationship("AreaOfInterest", back_populates="lulc_classifications")
    analysis = relationship("RasterAnalysis", back_populates="lulc_classifications")

# ============================================================
# REPORTS & EXPORTS
# ============================================================

class GeneratedReport(Base):
    __tablename__ = "generated_reports"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False)
    area_id = Column(UUID(as_uuid=True), ForeignKey("areas_of_interest.id"), nullable=False)
    analysis_id = Column(UUID(as_uuid=True), ForeignKey("raster_analysis.id"), nullable=False)
    
    report_type = Column(String(50))  # pdf, html, json
    title = Column(String(255))
    description = Column(Text)
    
    s3_path = Column(Text, nullable=False)
    thumbnail_path = Column(Text)
    
    generated_at = Column(DateTime, default=datetime.utcnow)
    file_size_mb = Column(Float)
    
    metadata = Column(JSONB)
    
    # Relationships
    user = relationship("User", back_populates="reports")
    analysis = relationship("RasterAnalysis", back_populates="reports")
    
    # Indexes
    __table_args__ = (
        Index('idx_report_user', 'user_id', 'generated_at'),
    )

# ============================================================
# NOTIFICATIONS
# ============================================================

class UserNotification(Base):
    __tablename__ = "user_notifications"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    
    notification_type = Column(String(50))  # analysis_complete, fire_alert, report_ready
    title = Column(String(255))
    message = Column(Text)
    
    related_area_id = Column(UUID(as_uuid=True), ForeignKey("areas_of_interest.id"))
    related_analysis_id = Column(UUID(as_uuid=True), ForeignKey("raster_analysis.id"))
    
    is_read = Column(Boolean, default=False)
    read_at = Column(DateTime)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # Relationships
    user = relationship("User", back_populates="notifications")
    
    # Indexes
    __table_args__ = (
        Index('idx_notification_user', 'user_id', 'is_read'),
    )

# ============================================================
# AUDIT LOG
# ============================================================

class AuditLog(Base):
    __tablename__ = "audit_logs"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id"))
    action = Column(String(100))  # create_aoi, run_analysis, delete_report
    resource_type = Column(String(50))
    resource_id = Column(UUID(as_uuid=True))
    
    changes = Column(JSONB)
    ip_address = Column(String(50))
    user_agent = Column(Text)
    
    created_at = Column(DateTime, default=datetime.utcnow, index=True)
    
    # Indexes
    __table_args__ = (
        Index('idx_audit_user_action', 'user_id', 'action'),
    )
