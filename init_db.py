"""Script to initialize the database with sample data"""

import asyncio
import logging
from app.database import SessionLocal, init_db
from app.models import Summary
from datetime import datetime

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


async def init_sample_data():
    """Initialize database with sample data"""
    try:
        # Initialize tables with retry logic
        logger.info("Initializing database...")
        await init_db()
        logger.info("✓ Database initialized")
        
        # Create a session
        session = SessionLocal()
        
        try:
            # Check if sample data already exists
            existing = session.query(Summary).first()
            if existing:
                logger.info("Sample data already exists, skipping")
                return
            
            # Add sample data
            sample_summary = Summary(
                documento_id=1,
                texto_original="Este es un documento de ejemplo con mucho texto para demostrar "
                              "la funcionalidad del servicio de resúmenes. El texto debe ser lo "
                              "suficientemente largo para poder ser resumido de manera efectiva. "
                              "Este es un documento de ejemplo con mucho texto para demostrar "
                              "la funcionalidad del servicio de resúmenes.",
                resumen="Documento de ejemplo para demostrar la funcionalidad del servicio de resúmenes.",
                longitud_resumen=85,
                tokens_utilizados=50,
                modelo="gemma4-26b-16g",
            )
            
            session.add(sample_summary)
            session.commit()
            
            logger.info(f"✓ Sample data initialized. Summary ID: {sample_summary.id}")
        finally:
            session.close()
        
    except Exception as e:
        logger.error(f"✗ Error initializing sample data: {type(e).__name__}")
        raise


if __name__ == "__main__":
    asyncio.run(init_sample_data())
