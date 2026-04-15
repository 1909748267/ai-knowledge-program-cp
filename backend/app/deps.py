from fastapi import Depends
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer

from app.auth import JwtService
from app.errors import AppError
from app.services.learning_service import LearningService
from app.services.quiz_service import QuizService
from app.services.user_service import UserService


def get_quiz_service() -> QuizService:
    return QuizService()


def get_user_service() -> UserService:
    return UserService()


def get_learning_service() -> LearningService:
    return LearningService()


bearer_scheme = HTTPBearer(auto_error=False)


def get_current_user(
    credentials: HTTPAuthorizationCredentials | None = Depends(bearer_scheme),
) -> dict:
    if credentials is None or not credentials.credentials:
        raise AppError(code="UNAUTHORIZED", message="请先登录", status_code=401)

    jwt_service = JwtService()
    payload = jwt_service.decode_token(credentials.credentials)
    subject = payload.get("sub")
    if subject is None:
        raise AppError(code="INVALID_TOKEN", message="无效登录态", status_code=401)

    try:
        user_id = int(subject)
    except (TypeError, ValueError) as exc:
        raise AppError(code="INVALID_TOKEN", message="无效登录态", status_code=401) from exc

    user_service = UserService()
    return user_service.get_user_by_id(user_id)
