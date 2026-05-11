"""Routes for summaries API endpoints"""

from fastapi import APIRouter, HTTPException, status
from pydantic import BaseModel
from typing import Optional, Any
from app.services.summary_service import SummaryService

summaries_router = APIRouter()
summary_service = SummaryService()

#TODO:este ponerlo en models
class SummaryResponse(BaseModel):
    success: bool
    data: Optional[Any] = None
    message: Optional[str] = None
    documento_id: Optional[int] = None

#TODO:a este le fallta un formato
@summaries_router.get("/document/{document_id}", response_model=SummaryResponse)
async def get_document_summary(document_id: int):
    try:
        summary = summary_service.get_by_id(document_id)
        return SummaryResponse(success=True, data=summary)
    except ValueError as exc:
        #TODO:aplicar RFC9457, tambien agregar un log de que no salio por el lugar indicado
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail={
                "success": False,
                "message": str(exc),
                "documento_id": document_id,
            }
        )