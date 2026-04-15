from fastapi import APIRouter, Depends

from app.deps import get_current_user, get_user_service
from app.schemas import SuccessResponse, UpdateUserRequest
from app.services.user_service import UserService

router = APIRouter(prefix="/api/users", tags=["users"])


@router.get("/me", response_model=SuccessResponse)
def get_me(current_user: dict = Depends(get_current_user)) -> SuccessResponse:
    return SuccessResponse(data=current_user)


@router.patch("/me", response_model=SuccessResponse)
def update_me(
    request: UpdateUserRequest,
    current_user: dict = Depends(get_current_user),
    user_service: UserService = Depends(get_user_service),
) -> SuccessResponse:
    user = user_service.update_user(
        user_id=current_user["id"],
        nickname=request.nickname,
        avatar_url=request.avatar_url,
    )
    return SuccessResponse(data={"success": True, "user": user})
