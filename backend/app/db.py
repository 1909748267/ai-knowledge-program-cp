from functools import lru_cache

from sqlalchemy import create_engine
from sqlalchemy.engine import Engine

from app.config import get_settings
from app.errors import AppError


@lru_cache(maxsize=1)
def get_engine() -> Engine:
    settings = get_settings()
    if not settings.db_dsn:
        raise AppError(code="DB_DSN_MISSING", message="未配置 DB_DSN", status_code=500)

    return create_engine(
        settings.db_dsn,
        pool_pre_ping=True,
        future=True,
    )
