"""
FastAPI application entry point for Summary Service.
"""

from __future__ import annotations

import logging
from contextlib import asynccontextmanager

from fastapi import FastAPI, Request
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse

from app.database import init_db
from app.routers import router
from config import settings


# Configure logging
logging.basicConfig(level=settings.LOG_LEVEL)
logger = logging.getLogger(__name__)


# Lifecycle management
@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Manage application lifecycle - startup and shutdown
    """
    # Startup
    logger.info("Starting Summary Service...")
    try:
        init_db()
        logger.info("Database initialized successfully")
    except Exception as e:
        logger.error(f"Failed to initialize database: {e}")
    
    yield
    
    # Shutdown
    logger.info("Shutting down Summary Service...")


# Create FastAPI application
app = FastAPI(
    title="Summary Service",
    version="1.0.0",
    description="Microservice for document summarization using AI (Gemma4)",
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
async def health_check():
    """Service health check"""
    return {
        "status": "healthy",
        "service": "Summary Service",
        "version": "1.0.0"
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
