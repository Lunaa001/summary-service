"""
FastAPI application entry point for Summary Service.
"""

from __future__ import annotations

import logging
from contextlib import asynccontextmanager

from fastapi import FastAPI, Request, HTTPException, status
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse

from app.database import init_db, check_db
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
    
    If database initialization fails, the application will not start.
    This ensures the app never runs without a valid database connection.
    """
    # Startup
    logger.info("Starting Summary Service...")
    try:
        await init_db()
        logger.info("✓ Database initialized and ready")
    except Exception as e:
        # Don't catch the exception - let it propagate to prevent app startup
        logger.critical("✗ Failed to initialize database. Application cannot start.")
        raise
    
    yield
    
    # Shutdown
    logger.info("Shutting down Summary Service...")


# Create FastAPI application
app = FastAPI(
    title="Summary Service",
    version="1.0.0",
    description="Microservice for document summarization using AI (Groq - llama-3.3-70b)",
    lifespan=lifespan,
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
@app.get("/health")
async def health_check(deep: bool = False):
    """Service health check"""
    components = {
        "database": "unknown",
        "ai": "skipped",
    }
    
    try:
        check_db()
        components["database"] = "ok"
    except Exception:
        components["database"] = "error"
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail={
                "status": "unhealthy",
                "service": "Summary Service",
                "version": "1.0.0",
                "components": components,
            },
        )
    
    if deep or settings.HEALTHCHECK_AI:
        try:
            AIService().test_connection()
            components["ai"] = "ok"
        except Exception:
            components["ai"] = "error"
            raise HTTPException(
                status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                detail={
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


@app.get("/")
async def root():
    """Root endpoint"""
    return {
        "message": "Summary Service API",
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
