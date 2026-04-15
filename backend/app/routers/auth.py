from fastapi import APIRouter, Depends

from app.deps import get_user_service
from app.schemas import SuccessResponse, WechatLoginRequest
from app.services.user_service import UserService

router = APIRouter(prefix="/api/auth", tags=["auth"])


@router.post("/wechat/login", response_model=SuccessResponse)
def wechat_login(
    request: WechatLoginRequest,
    user_service: UserService = Depends(get_user_service),
) -> SuccessResponse:
    data = user_service.login_by_wechat_code(request.code)
    return SuccessResponse(data=data)


@router.post("/logout", response_model=SuccessResponse)
def logout() -> SuccessResponse:
    return SuccessResponse(data={"success": True})
