from fastapi import FastAPI
from fastapi.exceptions import RequestValidationError
from fastapi.middleware.cors import CORSMiddleware
from typing import Any, cast

from app.config import get_settings
from app.errors import AppError, app_error_handler, validation_error_handler
from app.routers.auth import router as auth_router
from app.routers.health import router as health_router
from app.routers.history import router as history_router
from app.routers.quiz import router as quiz_router
from app.routers.users import router as users_router
from app.routers.wrongbook import router as wrongbook_router


def create_app() -> FastAPI:
    settings = get_settings()

    app = FastAPI(title=settings.app_name, version=settings.app_version)

    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.cors_origins_list,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    app.add_exception_handler(AppError, cast(Any, app_error_handler))
    app.add_exception_handler(RequestValidationError, cast(Any, validation_error_handler))

    app.include_router(health_router)
    app.include_router(auth_router)
    app.include_router(users_router)
    app.include_router(quiz_router)
    app.include_router(history_router)
    app.include_router(wrongbook_router)

    return app


app = create_app()
