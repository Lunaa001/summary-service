"""
Summary Service - Handles document summarization via AI.
This service ONLY generates summaries. It does NOT persist data.
Persistence is handled by the persistence-service.
"""
import logging
from typing import Optional
from app.services.ai_service import AIService
from config import settings

logger = logging.getLogger(__name__)


class SummaryService:
    """Service for generating document summaries — no database, no persistence"""
    
    def __init__(self, ai_service: AIService = None):
        """
        Initialize SummaryService
        
        Args:
            ai_service: AIService instance (optional for dependency injection)
        """
        self.ai_service = ai_service
    
    def generate_summary(self, document_text: str, documento_id: str = None, max_tokens: int = None) -> dict:
        """
        Generate a concise summary of document text using Groq API (llama-3.3-70b)
        
        Args:
            document_text: Full text extracted from document
            documento_id: ID of the document (optional, for tracking)
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
            
            return {
                "document_id": documento_id,
                "summary": summary_text,
                "longitud_resumen": len(summary_text),
                "modelo": settings.GROQ_MODEL,
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
