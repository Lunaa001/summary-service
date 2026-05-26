"""
Summary Service - Handles document summarization via AI with database persistence
"""
import logging
from typing import Optional
from sqlalchemy.orm import Session
from app.services.ai_service import AIService
from app.models.summary import Summary
from config import settings

logger = logging.getLogger(__name__)


class SummaryService:
    """Service for generating and managing document summaries"""
    
    def __init__(self, ai_service: AIService = None, db_session: Session = None):
        """
        Initialize SummaryService
        
        Args:
            ai_service: AIService instance (optional for dependency injection)
            db_session: Database session (optional for dependency injection)
        """
        self.ai_service = ai_service
        self.db_session = db_session
    
    def generate_summary(self, document_text: str, documento_id: int, max_tokens: int = None) -> dict:
        """
        Generate a concise summary of document text using Gemma4 API
        
        Args:
            document_text: Full text extracted from document
            documento_id: ID of the document
            max_tokens: Maximum tokens for summary (default from config)
            
        Returns:
            Dictionary with summary data
            
        Raises:
            ValueError: If text is empty or too short
            RuntimeError: If AI service is not initialized
        """
        if not document_text or not document_text.strip():
            raise ValueError("Document text cannot be empty")
        
        if not self.ai_service:
            raise RuntimeError("AIService not initialized. Cannot generate summary.")
        
        max_tokens = max_tokens or settings.DEFAULT_MAX_TOKENS
        
        logger.info(f"Generating summary for document {documento_id} ({len(document_text)} characters)")
        
        try:
            summary_text = self.ai_service.generate_summary(
                text=document_text,
                max_tokens=max_tokens
            )
            logger.info(f"Summary generated: {len(summary_text)} characters")
            
            # Save to database if session available
            if self.db_session:
                summary_record = self._save_summary(
                    documento_id=documento_id,
                    texto_original=document_text,
                    resumen=summary_text
                )
                return {
                    "id": summary_record.id,
                    "documento_id": summary_record.documento_id,
                    "resumen": summary_record.resumen,
                    "longitud_resumen": summary_record.longitud_resumen,
                }
            
            return {
                "documento_id": documento_id,
                "resumen": summary_text,
                "longitud_resumen": len(summary_text),
            }
        except Exception as e:
            logger.error(f"Error generating summary: {str(e)}")
            raise
    
    def should_generate_summary(self, document_text: str, min_length: int = None) -> bool:
        """
        Determine if a document should be summarized (quality check)
        
        Args:
            document_text: Document text to check
            min_length: Minimum length required (default from config)
            
        Returns:
            True if document meets criteria for summarization
        """
        if not document_text:
            return False
        
        min_length = min_length or settings.MIN_TEXT_LENGTH
        clean_text = document_text.strip()
        return len(clean_text) >= min_length
    
    def _save_summary(self, documento_id: int, texto_original: str, resumen: str) -> Summary:
        """
        Save summary to database
        
        Args:
            documento_id: Document ID
            texto_original: Original document text
            resumen: Generated summary
            
        Returns:
            Summary record
        """
        summary_record = Summary(
            documento_id=documento_id,
            texto_original=texto_original,
            resumen=resumen,
            longitud_resumen=len(resumen),
            modelo=settings.IA_MODEL,
        )
        self.db_session.add(summary_record)
        self.db_session.commit()
        self.db_session.refresh(summary_record)
        return summary_record
    
    def get_by_documento_id(self, documento_id: int) -> Optional[dict]:
        """
        Get summary by document ID
        
        Args:
            documento_id: Document ID
            
        Returns:
            Summary dictionary or None if not found
            
        Raises:
            RuntimeError: If database session not available
        """
        if not self.db_session:
            raise RuntimeError("Database session not available")
        
        try:
            summary = self.db_session.query(Summary).filter(
                Summary.documento_id == documento_id
            ).first()
            
            if not summary:
                raise ValueError(f"Summary not found for document {documento_id}")
            
            return {
                "id": summary.id,
                "documento_id": summary.documento_id,
                "resumen": summary.resumen,
                "longitud_resumen": summary.longitud_resumen,
                "fecha_creacion": summary.fecha_creacion.isoformat() if summary.fecha_creacion else None,
            }
        except Exception as e:
            logger.error(f"Error retrieving summary: {str(e)}")
            raise
    
    def get_by_id(self, summary_id: int) -> Optional[dict]:
        """
        Get summary by ID
        
        Args:
            summary_id: Summary ID
            
        Returns:
            Summary dictionary or None if not found
            
        Raises:
            RuntimeError: If database session not available
        """
        if not self.db_session:
            raise RuntimeError("Database session not available")
        
        try:
            summary = self.db_session.query(Summary).filter(
                Summary.id == summary_id
            ).first()
            
            if not summary:
                raise ValueError(f"Summary not found with id {summary_id}")
            
            return {
                "id": summary.id,
                "documento_id": summary.documento_id,
                "resumen": summary.resumen,
                "longitud_resumen": summary.longitud_resumen,
                "fecha_creacion": summary.fecha_creacion.isoformat() if summary.fecha_creacion else None,
            }
        except Exception as e:
            logger.error(f"Error retrieving summary: {str(e)}")
            raise
