"""Routes for summaries API endpoints.
Summary Service only generates summaries — no DB persistence here.
"""

from fastapi import APIRouter, HTTPException, status
from pydantic import BaseModel, Field
from typing import Optional

from app.services.summary_service import SummaryService
from app.services.ai_service import AIService

summaries_router = APIRouter(prefix="/summaries", tags=["summaries"])


# ============================================================================
# REQUEST / RESPONSE MODELS
# ============================================================================

class SummaryGenerationRequest(BaseModel):
    """Request model for generating a summary"""
    document_id: Optional[str] = Field(None, description="UUID of the document")
    texto: str = Field(..., min_length=1, description="Text to summarize")
    filename: Optional[str] = Field(None, description="Original filename")
    job_id: Optional[str] = Field(None, description="Job ID for tracking")
    max_tokens: Optional[int] = Field(None, ge=100, le=4096, description="Max tokens for summary")


class SummaryGenerationResponse(BaseModel):
    """Response model — matches the standardized output format"""
    document_id: Optional[str] = None
    filename: Optional[str] = None
    job_id: Optional[str] = None
    summary: str
    modelo: Optional[str] = None


# ============================================================================
# ENDPOINTS
# ============================================================================

@summaries_router.post(
    "/generate",
    response_model=SummaryGenerationResponse,
    status_code=status.HTTP_200_OK,
    summary="Generate a summary from text",
    description="Receives extracted text and returns an AI-generated summary. "
                "This service does NOT persist data — persistence is handled by persistence-service.",
)
def generate_summary(request: SummaryGenerationRequest):
    """
    Generate a summary for a document.
    
    This endpoint ONLY generates summaries using AI. It does not:
    - Save anything to a database
    - Look up existing summaries
    - Interact with any other service
    
    Args:
        request: SummaryGenerationRequest with texto and optional metadata
        
    Returns:
        SummaryGenerationResponse with the generated summary
    """
    try:
        if not request.texto or not request.texto.strip():
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail={
                    "success": False,
                    "message": "Document text cannot be empty",
                    "document_id": request.document_id,
                }
            )
        
        # Initialize services
        ai_service = AIService()
        summary_service = SummaryService(ai_service=ai_service)
        
        # Check if text is long enough
        if not summary_service.should_generate_summary(request.texto):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail={
                    "success": False,
                    "message": "Document text is too short to summarize",
                    "document_id": request.document_id,
                }
            )
        
        # Generate summary (no DB involved)
        result = summary_service.generate_summary(
            document_text=request.texto,
            documento_id=request.document_id,
            max_tokens=request.max_tokens
        )
        
        return SummaryGenerationResponse(
            document_id=request.document_id,
            filename=request.filename,
            job_id=request.job_id,
            summary=result["summary"],
            modelo=result.get("modelo"),
        )
    
    except HTTPException:
        raise
    except ValueError as exc:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail={
                "success": False,
                "message": str(exc),
                "document_id": request.document_id,
            }
        )
    except Exception as exc:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail={
                "success": False,
                "message": "Error generating summary",
                "document_id": request.document_id,
            }
        )
