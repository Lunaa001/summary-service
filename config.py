"""Configuration settings for Summary Service"""

import os
from pydantic_settings import BaseSettings
from pydantic import ConfigDict


class Settings(BaseSettings):
    """Application settings"""
    
    model_config = ConfigDict(
        env_file=".env",
        case_sensitive=True,
        extra="ignore",
    )
    
    # Database
    DATABASE_URL: str = os.getenv(
        "DATABASE_URL",
        "postgresql://postgres:postgres@postgres:5432/summary_service"
    )
    
    # AI Service
    MODEL_API_KEY: str = os.getenv("MODEL_API_KEY", "")
    MODEL_API_BASE_URL: str = os.getenv(
        "MODEL_API_BASE_URL",
        "https://ai.cloud.um.edu.ar/api/v1"
    )
    IA_MODEL: str = os.getenv("IA_MODEL", "gemma4-26b-16g")
    
    # Summary settings
    DEFAULT_MAX_TOKENS: int = 300
    MIN_TEXT_LENGTH: int = 100
    
    # Service ports and hosts
    HOST: str = os.getenv("HOST", "0.0.0.0")
    PORT: int = int(os.getenv("PORT", "8002"))
    
    # Logging
    LOG_LEVEL: str = os.getenv("LOG_LEVEL", "INFO")


settings = Settings()
