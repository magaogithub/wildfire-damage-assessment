"""
Application Configuration
Manages environment variables and settings
"""

from pydantic_settings import BaseSettings
from typing import List
import json

class Settings(BaseSettings):
    # ============================================================
    # APPLICATION
    # ============================================================
    APP_NAME: str = "Wildfire Damage Assessment Platform"
    APP_VERSION: str = "1.0.0"
    ENVIRONMENT: str = "development"
    DEBUG: bool = True
    
    # ============================================================
    # BACKEND
    # ============================================================
    BACKEND_URL: str = "http://localhost:8000"
    API_V1_STR: str = "/api/v1"
    
    # ============================================================
    # DATABASE
    # ============================================================
    DATABASE_URL: str = "postgresql://postgres:postgres@localhost:5432/wildfire_db"
    DATABASE_ECHO: bool = False
    SQLALCHEMY_POOL_SIZE: int = 20
    SQLALCHEMY_MAX_OVERFLOW: int = 40
    
    # ============================================================
    # REDIS
    # ============================================================
    REDIS_URL: str = "redis://localhost:6379/0"
    REDIS_CACHE_TTL: int = 300
    
    # ============================================================
    # JWT AUTHENTICATION
    # ============================================================
    SECRET_KEY: str = "your-super-secret-key-change-in-production"
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    REFRESH_TOKEN_EXPIRE_DAYS: int = 7
    
    # ============================================================
    # AWS
    # ============================================================
    AWS_REGION: str = "us-east-1"
    AWS_ACCESS_KEY_ID: str = ""
    AWS_SECRET_ACCESS_KEY: str = ""
    S3_BUCKET: str = "wildfire-data"
    
    # ============================================================
    # SENTINEL HUB
    # ============================================================
    SENTINEL_HUB_CLIENT_ID: str = ""
    SENTINEL_HUB_CLIENT_SECRET: str = ""
    SENTINEL_HUB_INSTANCE_ID: str = ""
    
    # ============================================================
    # GOOGLE EARTH ENGINE
    # ============================================================
    GEE_PROJECT_ID: str = ""
    GEE_SERVICE_ACCOUNT_KEY: str = ""
    
    # ============================================================
    # CELERY
    # ============================================================
    CELERY_BROKER_URL: str = "redis://localhost:6379/1"
    CELERY_RESULT_BACKEND: str = "redis://localhost:6379/2"
    CELERY_TASK_SERIALIZER: str = "json"
    CELERY_ACCEPT_CONTENT: str = "json"
    CELERY_TIMEZONE: str = "UTC"
    
    # ============================================================
    # CORS
    # ============================================================
    CORS_ORIGINS: List[str] = [
        "http://localhost:3000",
        "http://localhost:8000",
        "http://localhost:5173"
    ]
    ALLOWED_HOSTS: List[str] = ["localhost", "127.0.0.1"]
    
    # ============================================================
    # EMAIL
    # ============================================================
    SMTP_SERVER: str = "smtp.gmail.com"
    SMTP_PORT: int = 587
    SMTP_USER: str = ""
    SMTP_PASSWORD: str = ""
    SMTP_FROM: str = "noreply@wildfire-platform.com"
    
    # ============================================================
    # LOGGING
    # ============================================================
    LOG_LEVEL: str = "INFO"
    LOG_FILE: str = "logs/app.log"
    
    # ============================================================
    # FILE UPLOADS
    # ============================================================
    MAX_UPLOAD_SIZE_MB: int = 500
    UPLOAD_DIR: str = "uploads/"
    TEMP_DATA_DIR: str = "temp/"
    
    # ============================================================
    # ML MODELS
    # ============================================================
    YOLO_BUILDING_MODEL_PATH: str = "ml_models/building_detector.pt"
    DAMAGE_CLASSIFIER_PATH: str = "ml_models/damage_classifier.pt"
    
    class Config:
        env_file = ".env"
        case_sensitive = True

settings = Settings()
