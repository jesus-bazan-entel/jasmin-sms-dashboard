"""
Configuration settings for Jasmin SMS Dashboard
"""
from pydantic import Field, field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict
from typing import List, Optional, Any
import os
from pathlib import Path

class Settings(BaseSettings):
    """Application settings"""

    # This is the new Pydantic v2 configuration method
    model_config = SettingsConfigDict(
        env_file=".env",
        case_sensitive=True,
        extra='ignore'
    )

    # Application
    APP_NAME: str = "Jasmin SMS Dashboard"
    VERSION: str = "2.0.0"
    DEBUG: bool = Field(default=False, env="DEBUG")
    HOST: str = Field(default="0.0.0.0", env="HOST")
    PORT: int = Field(default=8000, env="PORT")

    # Security
    SECRET_KEY: str = Field(..., env="SECRET_KEY")
    ACCESS_TOKEN_EXPIRE_MINUTES: int = Field(default=30, env="ACCESS_TOKEN_EXPIRE_MINUTES")
    REFRESH_TOKEN_EXPIRE_DAYS: int = Field(default=7, env="REFRESH_TOKEN_EXPIRE_DAYS")
    ALGORITHM: str = "HS256"

    # CORS
    ALLOWED_HOSTS: List[str] = Field(
        default=["http://localhost:3000", "http://127.0.0.1:3000"],
        env="ALLOWED_HOSTS"
    )

    # Database
    DATABASE_URL: str = Field(..., env="DATABASE_URL")
    DATABASE_ECHO: bool = Field(default=False, env="DATABASE_ECHO")

    # Redis
    REDIS_URL: str = Field(default="redis://localhost:6379/0", env="REDIS_URL")

    # Jasmin SMS Gateway Configuration
    JASMIN_HOST: str = Field(default="localhost", env="JASMIN_HOST")
    JASMIN_TELNET_PORT: int = Field(default=8990, env="JASMIN_TELNET_PORT")
    JASMIN_HTTP_PORT: int = Field(default=1401, env="JASMIN_HTTP_PORT")
    JASMIN_USERNAME: str = Field(..., env="JASMIN_USERNAME")
    JASMIN_PASSWORD: str = Field(..., env="JASMIN_PASSWORD")
    JASMIN_TIMEOUT: int = Field(default=30, env="JASMIN_TIMEOUT")

    # SMS Configuration
    DEFAULT_SENDER_ID: str = Field(default="SMS", env="DEFAULT_SENDER_ID")
    SMS_RATE_LIMIT: int = Field(default=100, env="SMS_RATE_LIMIT")  # per minute
    SMS_BATCH_SIZE: int = Field(default=1000, env="SMS_BATCH_SIZE")

    # Email Configuration
    SMTP_HOST: str = Field(default="localhost", env="SMTP_HOST")
    SMTP_PORT: int = Field(default=587, env="SMTP_PORT")
    SMTP_USERNAME: Optional[str] = Field(default=None, env="SMTP_USERNAME")
    SMTP_PASSWORD: Optional[str] = Field(default=None, env="SMTP_PASSWORD")
    SMTP_USE_TLS: bool = Field(default=True, env="SMTP_USE_TLS")
    FROM_EMAIL: str = Field(default="noreply@jasmin-dashboard.com", env="FROM_EMAIL")

    # File Storage
    UPLOAD_DIR: str = Field(default="uploads", env="UPLOAD_DIR")
    MAX_FILE_SIZE: int = Field(default=10 * 1024 * 1024, env="MAX_FILE_SIZE")  # 10MB
    ALLOWED_FILE_TYPES: List[str] = Field(
        default=["csv", "xlsx", "xls", "txt"],
        env="ALLOWED_FILE_TYPES"
    )

    # Logging
    LOG_LEVEL: str = Field(default="INFO", env="LOG_LEVEL")
    LOG_FILE: str = Field(default="logs/jasmin-dashboard.log", env="LOG_FILE")
    LOG_MAX_SIZE: int = Field(default=10 * 1024 * 1024, env="LOG_MAX_SIZE")  # 10MB
    LOG_BACKUP_COUNT: int = Field(default=5, env="LOG_BACKUP_COUNT")

    # Analytics
    ANALYTICS_RETENTION_DAYS: int = Field(default=365, env="ANALYTICS_RETENTION_DAYS")
    METRICS_UPDATE_INTERVAL: int = Field(default=1, env="METRICS_UPDATE_INTERVAL")  # seconds

    # Webhooks
    WEBHOOK_TIMEOUT: int = Field(default=30, env="WEBHOOK_TIMEOUT")
    WEBHOOK_RETRY_ATTEMPTS: int = Field(default=3, env="WEBHOOK_RETRY_ATTEMPTS")

    # Billing
    DEFAULT_CURRENCY: str = Field(default="USD", env="DEFAULT_CURRENCY")
    SMS_COST_PER_MESSAGE: float = Field(default=0.01, env="SMS_COST_PER_MESSAGE")

    # API Rate Limiting
    API_RATE_LIMIT: int = Field(default=1000, env="API_RATE_LIMIT")  # requests per hour

    # Background Tasks
    CELERY_BROKER_URL: str = Field(default="redis://localhost:6379/1", env="CELERY_BROKER_URL")
    CELERY_RESULT_BACKEND: str = Field(default="redis://localhost:6379/2", env="CELERY_RESULT_BACKEND")

    # This is the new Pydantic v2 validator syntax
    @field_validator("ALLOWED_HOSTS", "ALLOWED_FILE_TYPES", mode='before')
    @classmethod
    def parse_comma_separated_list(cls, v: Any) -> List[str]:
        if isinstance(v, str):
            return [item.strip() for item in v.split(",") if item.strip()]
        elif isinstance(v, list):
            return v
        return []

# Create settings instance with error handling
try:
    settings = Settings()
except Exception as e:
    print(f"Error loading settings: {e}")
    # Create settings with defaults if .env fails
    settings = Settings(
        SECRET_KEY="fallback-secret-key-change-this",
        DATABASE_URL="postgresql+asyncpg://jasmin_user:jasmin_password@localhost:5432/jasmin_sms_db",
        JASMIN_USERNAME="jcliadmin",
        JASMIN_PASSWORD="jclipwd"
    )

# Create necessary directories
def create_directories():
    """Create necessary directories if they don't exist"""
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
