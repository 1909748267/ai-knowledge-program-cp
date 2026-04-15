from datetime import datetime, timedelta, timezone
from typing import Dict

import jwt
from jwt import ExpiredSignatureError, InvalidTokenError

from app.config import get_settings
from app.errors import AppError


class JwtService:
    def __init__(self) -> None:
        self.settings = get_settings()
        if not self.settings.jwt_secret:
            raise AppError(code="JWT_SECRET_MISSING", message="未配置 JWT_SECRET", status_code=500)

    def issue_token(self, user_id: int) -> str:
        now = datetime.now(timezone.utc)
        payload: Dict[str, object] = {
            "sub": str(user_id),
            "iat": now,
            "exp": now + timedelta(seconds=self.settings.access_token_ttl),
        }
        return jwt.encode(payload, self.settings.jwt_secret, algorithm=self.settings.jwt_algorithm)

    def decode_token(self, token: str) -> Dict:
        try:
            payload = jwt.decode(
                token,
                self.settings.jwt_secret,
                algorithms=[self.settings.jwt_algorithm],
                options={"require": ["exp", "sub"]},
            )
        except ExpiredSignatureError as exc:
            raise AppError(code="TOKEN_EXPIRED", message="登录已过期，请重新登录", status_code=401) from exc
        except InvalidTokenError as exc:
            raise AppError(code="INVALID_TOKEN", message="无效登录态", status_code=401) from exc

        return payload
