from datetime import datetime, timedelta, timezone

import jwt

from app.auth import JwtService
from app.config import get_settings
from app.errors import AppError


def test_jwt_token_expired_should_raise(monkeypatch):
    monkeypatch.setenv("JWT_SECRET", "unit-test-secret")
    monkeypatch.setenv("JWT_ALGORITHM", "HS256")
    get_settings.cache_clear()

    jwt_service = JwtService()
    token = jwt.encode(
        {
            "sub": "1",
            "exp": datetime.now(timezone.utc) - timedelta(seconds=1),
        },
        "unit-test-secret",
        algorithm="HS256",
    )

    try:
        jwt_service.decode_token(token)
        assert False, "expected AppError"
    except AppError as exc:
        assert exc.code == "TOKEN_EXPIRED"
        assert exc.status_code == 401
    finally:
        get_settings.cache_clear()
