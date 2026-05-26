"""Configuration settings for Summary Service"""

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
    DATABASE_URL: str = "postgresql://postgres:postgres@postgres:5432/summary_service"
    
    # AI Service
    MODEL_API_KEY: str = ""
    MODEL_API_BASE_URL: str = "https://ai.cloud.um.edu.ar/api/v1"
    IA_MODEL: str = "gemma4-26b-16g"
    AI_CONNECT_TIMEOUT_SECONDS: int = 10
    AI_REQUEST_TIMEOUT_SECONDS: int = 30
    AI_HEALTHCHECK_TIMEOUT_SECONDS: int = 5
    
    # Summary settings
    DEFAULT_MAX_TOKENS: int = 300
    MIN_TEXT_LENGTH: int = 100
    
    # Service ports and hosts
    HOST: str = "0.0.0.0"
    PORT: int = 8002
    
    # Logging
    LOG_LEVEL: str = "INFO"

    # Database pool
    DB_POOL_SIZE: int = 5
    DB_MAX_OVERFLOW: int = 10
    
    # Healthcheck behavior
    HEALTHCHECK_AI: bool = False


settings = Settings()
