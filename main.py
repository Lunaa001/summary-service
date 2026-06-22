"""
FastAPI application entry point for Summary Service.
This service ONLY generates summaries — no database required.
"""

from __future__ import annotations

import logging
from contextlib import asynccontextmanager

from fastapi import FastAPI, Request
from fastapi.exceptions import RequestValidationError
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from app.services.ai_service import AIService
from app.routers import router
from config import settings


# Configure logging
logging.basicConfig(level=settings.LOG_LEVEL)
logger = logging.getLogger(__name__)


# Lifecycle management
@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Manage application lifecycle - startup and shutdown.
    No database initialization needed — this service only generates summaries.
    """
    # Startup
    logger.info("Starting Summary Service...")
    logger.info("✓ Summary Service ready (no database required)")

    # Load config from Consul KV and override settings
    from app.consul_registration import register_service, deregister_service, fetch_kv_config
    kv_config = fetch_kv_config("summary-service")
    if kv_config:
        for key, value in kv_config.items():
            if hasattr(settings, key):
                current = getattr(settings, key)
                try:
                    setattr(settings, key, type(current)(value))
                except (ValueError, TypeError):
                    setattr(settings, key, value)

    # Register — tags are read from Consul KV automatically (no hardcoded labels)
    register_service(
        service_name="summary-service",
        service_port=settings.PORT,
        health_check_path="/health",
    )

    yield

    # Shutdown — deregister from Consul
    deregister_service("summary-service", settings.PORT)
    logger.info("Shutting down Summary Service...")


# Create FastAPI application
app = FastAPI(
    title="Summary Service — NotebookUM",
    version="1.0.0",
    description=(
        "Microservice for document summarization using AI (Groq - llama-3.3-70b). "
        "This service ONLY generates summaries from text. "
        "It does NOT persist data — persistence is handled by persistence-service."
    ),
    lifespan=lifespan,
)

# CORS - allow all origins for microservice communication
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(router)


# Exception handlers
@app.exception_handler(RequestValidationError)
async def request_validation_exception_handler(
    _request: Request,
    exc: RequestValidationError,
) -> JSONResponse:
    """Handle validation errors"""
    detail = "; ".join(error["msg"] for error in exc.errors())
    return JSONResponse(
        status_code=422,
        content={
            "success": False,
            "message": "Validation error",
            "detail": detail,
        }
    )


# Health check endpoint
@app.get("/health", tags=["health"])
async def health_check(deep: bool = False):
    """Service health check"""
    components = {
        "ai": "skipped",
    }
    
    if deep or settings.HEALTHCHECK_AI:
        try:
            AIService().test_connection()
            components["ai"] = "ok"
        except Exception:
            components["ai"] = "error"
            return JSONResponse(
                status_code=503,
                content={
                    "status": "degraded",
                    "service": "Summary Service",
                    "version": "1.0.0",
                    "components": components,
                },
            )
    
    return {
        "status": "healthy",
        "service": "Summary Service",
        "version": "1.0.0",
        "components": components,
    }


@app.get("/", tags=["root"])
async def root():
    """Root endpoint"""
    return {
        "message": "Summary Service API — NotebookUM",
        "version": "1.0.0",
        "docs": "/docs"
    }


def main() -> None:
    """Main entry point for the service"""
    logger.info("Summary Service is configured and ready.")
    logger.info(f"Starting server on {settings.HOST}:{settings.PORT}")


if __name__ == "__main__":
    import uvicorn
    main()
    uvicorn.run(
        app,
        host=settings.HOST,
        port=settings.PORT,
        log_level=settings.LOG_LEVEL.lower(),
    )
