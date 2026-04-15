from fastapi import APIRouter, Depends, Query

from app.deps import get_current_user, get_learning_service
from app.schemas import SuccessResponse
from app.services.learning_service import LearningService

router = APIRouter(prefix="/api/wrongbook", tags=["wrongbook"])


@router.get("", response_model=SuccessResponse)
def list_wrongbook(
    cursor: int | None = Query(default=None),
    limit: int = Query(default=10, ge=1, le=20),
    current_user: dict = Depends(get_current_user),
    learning_service: LearningService = Depends(get_learning_service),
) -> SuccessResponse:
    data = learning_service.list_wrongbook(
        user_id=current_user["id"],
        cursor=cursor,
        limit=limit,
    )
    return SuccessResponse(data=data)
