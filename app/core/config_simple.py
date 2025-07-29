"""
Simplified configuration settings for Jasmin SMS Dashboard
"""
from pydantic_settings import BaseSettings
from typing import List, Optional
import os

class Settings(BaseSettings):
    """Simplified application settings"""

    # Application
    APP_NAME: str = "Jasmin SMS Dashboard"
    VERSION: str = "2.0.0"
    DEBUG: bool = True
    HOST: str = "0.0.0.0"
    PORT: int = 8000

    # Security
    SECRET_KEY: str = "your-super-secret-key-change-this-in-production-jasmin-sms-dashboard-2024"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    REFRESH_TOKEN_EXPIRE_DAYS: int = 7
    ALGORITHM: str = "HS256"

    # CORS - Simple list without parsing
    ALLOWED_HOSTS: List[str] = [
        "http://localhost:3000",
        "http://127.0.0.1:3000", 
        "http://190.105.244.174",
        "https://190.105.244.174",
        "*"  # Allow all for development
    ]

    # Database
    DATABASE_URL: str = "postgresql+asyncpg://jasmin_user:jasmin_password@localhost:5432/jasmin_sms_db"
    DATABASE_ECHO: bool = False

    # Redis
    REDIS_URL: str = "redis://localhost:6379/0"

    # Jasmin SMS Gateway Configuration
    JASMIN_HOST: str = "localhost"
    JASMIN_TELNET_PORT: int = 8990
    JASMIN_HTTP_PORT: int = 1401
    JASMIN_USERNAME: str = "jcliadmin"
    JASMIN_PASSWORD: str = "jclipwd"
    JASMIN_TIMEOUT: int = 30

    # SMS Configuration
    DEFAULT_SENDER_ID: str = "SMS"
    SMS_RATE_LIMIT: int = 100
    SMS_BATCH_SIZE: int = 1000

    # Email Configuration
    SMTP_HOST: str = "localhost"
    SMTP_PORT: int = 587
    SMTP_USERNAME: Optional[str] = None
    SMTP_PASSWORD: Optional[str] = None
    SMTP_USE_TLS: bool = True
    FROM_EMAIL: str = "noreply@jasmin-dashboard.com"

    # File Storage
    UPLOAD_DIR: str = "uploads"
    MAX_FILE_SIZE: int = 10 * 1024 * 1024  # 10MB
    ALLOWED_FILE_TYPES: List[str] = ["csv", "xlsx", "xls", "txt"]

    # Logging
    LOG_LEVEL: str = "INFO"
    LOG_FILE: str = "logs/jasmin-dashboard.log"
    LOG_MAX_SIZE: int = 10 * 1024 * 1024  # 10MB
    LOG_BACKUP_COUNT: int = 5

    # Analytics
    ANALYTICS_RETENTION_DAYS: int = 365
    METRICS_UPDATE_INTERVAL: int = 1

    # Webhooks
    WEBHOOK_TIMEOUT: int = 30
    WEBHOOK_RETRY_ATTEMPTS: int = 3

    # Billing
    DEFAULT_CURRENCY: str = "USD"
    SMS_COST_PER_MESSAGE: float = 0.01

    # API Rate Limiting
    API_RATE_LIMIT: int = 1000

    # Background Tasks
    CELERY_BROKER_URL: str = "redis://localhost:6379/1"
    CELERY_RESULT_BACKEND: str = "redis://localhost:6379/2"

    class Config:
        env_file = ".env"
        case_sensitive = True

# Create settings instance
settings = Settings()

# Create necessary directories
def create_directories():
    """Create necessary directories if they don't exist"""
    from pathlib import Path
    
    directories = [
        settings.UPLOAD_DIR,
        "logs",
        "exports", 
        "templates",
        "static"
    ]

    for directory in directories:
        Path(directory).mkdir(parents=True, exist_ok=True)

# Call on import
create_directories()