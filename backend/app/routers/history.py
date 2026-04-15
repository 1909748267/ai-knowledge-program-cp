from fastapi import APIRouter, Depends, Query

from app.deps import get_current_user, get_learning_service
from app.schemas import SuccessResponse
from app.services.learning_service import LearningService

router = APIRouter(prefix="/api/history", tags=["history"])


@router.get("", response_model=SuccessResponse)
def list_history(
    cursor: int | None = Query(default=None),
    limit: int = Query(default=10, ge=1, le=20),
    current_user: dict = Depends(get_current_user),
    learning_service: LearningService = Depends(get_learning_service),
) -> SuccessResponse:
    data = learning_service.list_history(
        user_id=current_user["id"],
        cursor=cursor,
        limit=limit,
    )
    return SuccessResponse(data=data)


@router.get("/{session_id}", response_model=SuccessResponse)
def history_detail(
    session_id: int,
    current_user: dict = Depends(get_current_user),
    learning_service: LearningService = Depends(get_learning_service),
) -> SuccessResponse:
    data = learning_service.get_history_detail(user_id=current_user["id"], session_id=session_id)
    return SuccessResponse(data=data)
