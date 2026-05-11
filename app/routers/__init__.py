"""Main router for summaries endpoints"""

from fastapi import APIRouter
from app.controllers.summaries import summaries_router

router = APIRouter()
router.include_router(summaries_router)

__all__ = ["router"]
