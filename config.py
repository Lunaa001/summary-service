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
    
    # AI Service - Groq Configuration
    GROQ_API_KEY: str = ""
    GROQ_MODEL: str = "llama-3.3-70b-versatile"
    AI_CONNECT_TIMEOUT_SECONDS: int = 10
    AI_REQUEST_TIMEOUT_SECONDS: int = 60
    AI_HEALTHCHECK_TIMEOUT_SECONDS: int = 5
    
    # Summary settings
    DEFAULT_MAX_TOKENS: int = 2048
    MIN_TEXT_LENGTH: int = 100
    
    # Service ports and hosts
    HOST: str = "0.0.0.0"
    PORT: int = 5000
    
    # Logging
    LOG_LEVEL: str = "INFO"
    
    # Healthcheck behavior
    HEALTHCHECK_AI: bool = False

    # Redis (para caché de resúmenes)
    REDIS_HOST: str = "redis"
    REDIS_PORT: int = 6379
    REDIS_PASSWORD: str = ""


settings = Settings()
