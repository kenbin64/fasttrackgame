"""
Configuration for ButterflyFx Server

Loads settings from environment variables with secure defaults.
"""

from pydantic_settings import BaseSettings
from typing import Optional
import os


class Settings(BaseSettings):
    """Application settings."""
    
    # Application
    APP_NAME: str = "ButterflyFx Server"
    APP_VERSION: str = "2.0.0"
    DEBUG: bool = False
    
    # Server
    HOST: str = "0.0.0.0"
    PORT: int = 8000
    WORKERS: int = 4
    
    # Security
    SECRET_KEY: str = "CHANGE_THIS_IN_PRODUCTION_TO_RANDOM_SECRET_KEY_MIN_32_CHARS"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60 * 24  # 24 hours
    REFRESH_TOKEN_EXPIRE_DAYS: int = 30
    
    # Database
    DATABASE_URL: str = "postgresql://butterflyfx:butterflyfx@localhost:5432/butterflyfx"
    DB_POOL_SIZE: int = 20
    DB_MAX_OVERFLOW: int = 40
    
    # Redis
    REDIS_URL: str = "redis://localhost:6379/0"
    REDIS_CACHE_TTL: int = 3600  # 1 hour
    
    # Rate Limiting
    RATE_LIMIT_ENABLED: bool = True
    RATE_LIMIT_PER_MINUTE: int = 100
    RATE_LIMIT_PER_HOUR: int = 1000
    
    # CORS
    CORS_ORIGINS: list = ["*"]  # Configure for production
    CORS_ALLOW_CREDENTIALS: bool = True
    
    # Monitoring
    PROMETHEUS_ENABLED: bool = True
    METRICS_SNAPSHOT_INTERVAL: int = 60  # seconds
    
    # Legal
    TOS_VERSION: str = "1.0.0"
    TOS_EFFECTIVE_DATE: str = "2026-02-09"
    
    # Email (for future email verification)
    SMTP_HOST: Optional[str] = None
    SMTP_PORT: Optional[int] = None
    SMTP_USER: Optional[str] = None
    SMTP_PASSWORD: Optional[str] = None
    SMTP_FROM: Optional[str] = None
    
    # Logging
    LOG_LEVEL: str = "INFO"
    LOG_FORMAT: str = "json"
    
    class Config:
        env_file = ".env"
        case_sensitive = True


# Global settings instance
settings = Settings()


# Validate critical settings
def validate_settings():
    """Validate critical settings on startup."""
    errors = []
    
    if settings.SECRET_KEY == "CHANGE_THIS_IN_PRODUCTION_TO_RANDOM_SECRET_KEY_MIN_32_CHARS":
        errors.append("⚠️  WARNING: Using default SECRET_KEY. Change this in production!")
    
    if len(settings.SECRET_KEY) < 32:
        errors.append("❌ ERROR: SECRET_KEY must be at least 32 characters")
    
    if settings.DEBUG and "postgresql" in settings.DATABASE_URL:
        errors.append("⚠️  WARNING: DEBUG mode enabled with production database")
    
    if errors:
        print("\n".join(errors))
        if any("ERROR" in e for e in errors):
            raise ValueError("Critical configuration errors detected")
    
    print(f"✅ Configuration validated successfully")
    print(f"   App: {settings.APP_NAME} v{settings.APP_VERSION}")
    print(f"   Database: {settings.DATABASE_URL.split('@')[1] if '@' in settings.DATABASE_URL else 'SQLite'}")
    print(f"   Redis: {settings.REDIS_URL}")
    print(f"   Rate Limiting: {'Enabled' if settings.RATE_LIMIT_ENABLED else 'Disabled'}")
    print(f"   Prometheus: {'Enabled' if settings.PROMETHEUS_ENABLED else 'Disabled'}")


