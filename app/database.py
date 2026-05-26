"""Database configuration and session management"""

import asyncio
import logging
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, Session
from sqlalchemy.exc import SQLAlchemyError, OperationalError
from app.models.base import Base
from config import settings

logger = logging.getLogger(__name__)

# Create engine
engine = create_engine(
    settings.DATABASE_URL,
    echo=False,
    pool_pre_ping=True,
    pool_size=10,
    max_overflow=20,
)

# Create session factory
SessionLocal = sessionmaker(
    autocommit=False,
    autoflush=False,
    bind=engine,
)


async def init_db(max_retries: int = 5, retry_delay: int = 2):
    """
    Initialize database tables with retry logic for PostgreSQL startup.
    
    Attempts to connect and initialize the database schema.
    Uses fixed-delay retries (not exponential backoff) suitable for development/testing.
    
    Connection verification (SELECT 1):
    - Verifies actual database connectivity before schema initialization
    - Allows fast failure if PostgreSQL is completely unavailable
    - Does NOT synchronize multiple instances (PostgreSQL handles that internally via IF NOT EXISTS)
    
    Args:
        max_retries: Maximum number of connection attempts (default: 5)
        retry_delay: Fixed delay in seconds between retries (default: 2)
        
    Raises:
        SQLAlchemyError: If all connection attempts fail
        OperationalError: If database operations fail
    """
    
    for attempt in range(1, max_retries + 1):
        try:
            logger.info(f"Database connection attempt {attempt}/{max_retries}...")
            
            # Verify connectivity - fail fast if PostgreSQL is unreachable
            with engine.connect() as conn:
                conn.execute("SELECT 1")
            
            # Initialize schema
            Base.metadata.create_all(bind=engine)
            logger.info("✓ Database initialized successfully")
            return
            
        except (OperationalError, SQLAlchemyError) as e:
            error_msg = type(e).__name__
            
            if attempt == max_retries:
                # All retries exhausted
                logger.error(
                    f"Failed to initialize database after {max_retries} attempts. "
                    f"Error type: {error_msg}. "
                    f"Check PostgreSQL is running and accessible."
                )
                raise
            
            # Retry with fixed delay - using asyncio.sleep() to not block event loop
            logger.warning(
                f"Database connection attempt {attempt} failed ({error_msg}). "
                f"Retrying in {retry_delay}s... (attempt {attempt + 1}/{max_retries})"
            )
            await asyncio.sleep(retry_delay)
            
        except Exception as e:
            # Unexpected error - don't retry
            logger.error(
                f"Unexpected error during database initialization: {type(e).__name__}. "
                f"This is likely a code issue, not a connection problem."
            )
            raise


def get_session() -> Session:
    """Get database session"""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
