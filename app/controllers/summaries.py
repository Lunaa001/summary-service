"""Routes for summaries API endpoints"""

from fastapi import APIRouter, HTTPException, status, Depends
from pydantic import BaseModel
from typing import Optional, Any
from sqlalchemy.orm import Session

from app.services.summary_service import SummaryService
from app.services.ai_service import AIService
from app.database import get_session

summaries_router = APIRouter(prefix="/summaries", tags=["summaries"])


# ============================================================================
# MODELS
# ============================================================================

class SummaryResponse(BaseModel):
    """Response model for summary operations"""
    success: bool
    data: Optional[Any] = None
    message: Optional[str] = None
    documento_id: Optional[int] = None


class SummaryGenerationRequest(BaseModel):
    """Request model for generating a summary"""
    documento_id: int
    texto: str
    max_tokens: Optional[int] = 300


class SummaryDetailResponse(BaseModel):
    """Response model for detailed summary"""
    id: int
    documento_id: int
    resumen: str
    longitud_resumen: int
    fecha_creacion: Optional[str] = None


# ============================================================================
# ENDPOINTS
# ============================================================================

@summaries_router.post("/generate", response_model=SummaryResponse, status_code=status.HTTP_201_CREATED)
def generate_summary(
    request: SummaryGenerationRequest,
    session: Session = Depends(get_session)
):
    """
    Generate a summary for a document
    
    Args:
        request: SummaryGenerationRequest with documento_id and texto
        session: Database session
        
    Returns:
        SummaryResponse with generated summary
    """
    try:
        if not request.texto or not request.texto.strip():
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail={
                    "success": False,
                    "message": "Document text cannot be empty",
                    "documento_id": request.documento_id,
                }
            )
        
        # Initialize services
        ai_service = AIService()
        summary_service = SummaryService(ai_service=ai_service, db_session=session)
        
        # Check if text is long enough
        if not summary_service.should_generate_summary(request.texto):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail={
                    "success": False,
                    "message": "Document text is too short to summarize",
                    "documento_id": request.documento_id,
                }
            )
        
        # Generate summary
        result = summary_service.generate_summary(
            document_text=request.texto,
            documento_id=request.documento_id,
            max_tokens=request.max_tokens
        )
        
        return SummaryResponse(
            success=True,
            data=result,
            documento_id=request.documento_id,
            message="Summary generated successfully"
        )
    
    except HTTPException:
        raise
    except ValueError as exc:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail={
                "success": False,
                "message": str(exc),
                "documento_id": request.documento_id,
            }
        )
    except Exception as exc:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail={
                "success": False,
                "message": "Error generating summary",
                "documento_id": request.documento_id,
            }
        )


@summaries_router.get("/document/{documento_id}", response_model=SummaryResponse)
def get_document_summary(
    documento_id: int,
    session: Session = Depends(get_session)
):
    """
    Get summary for a document by document ID
    
    Args:
        documento_id: Document ID
        session: Database session
        
    Returns:
        SummaryResponse with summary data
    """
    try:
        if documento_id <= 0:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail={
                    "success": False,
                    "message": "Invalid document ID",
                    "documento_id": documento_id,
                }
            )
        
        summary_service = SummaryService(db_session=session)
        summary = summary_service.get_by_documento_id(documento_id)
        
        return SummaryResponse(
            success=True,
            data=summary,
            documento_id=documento_id
        )
    
    except HTTPException:
        raise
    except ValueError as exc:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail={
                "success": False,
                "message": str(exc),
                "documento_id": documento_id,
            }
        )
    except Exception as exc:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail={
                "success": False,
                "message": "Error retrieving summary",
                "documento_id": documento_id,
            }
        )


@summaries_router.get("/{summary_id}", response_model=SummaryResponse)
def get_summary_by_id(
    summary_id: int,
    session: Session = Depends(get_session)
):
    """
    Get summary by summary ID
    
    Args:
        summary_id: Summary ID
        session: Database session
        
    Returns:
        SummaryResponse with summary data
    """
    try:
        if summary_id <= 0:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail={
                    "success": False,
                    "message": "Invalid summary ID",
                }
            )
        
        summary_service = SummaryService(db_session=session)
        summary = summary_service.get_by_id(summary_id)
        
        return SummaryResponse(
            success=True,
            data=summary,
        )
    
    except HTTPException:
        raise
    except ValueError as exc:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail={
                "success": False,
                "message": str(exc),
            }
        )
    except Exception as exc:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail={
                "success": False,
                "message": "Error retrieving summary",
            }
        )
