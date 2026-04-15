from datetime import datetime, timezone
from typing import Any, Dict

from sqlalchemy import text

from app.auth import JwtService
from app.db import get_engine
from app.errors import AppError
from app.services.wechat_service import WechatService


class UserService:
    def __init__(self, wechat_service: WechatService | None = None) -> None:
        self.engine = get_engine()
        self.jwt_service = JwtService()
        self.wechat_service = wechat_service or WechatService()

    def login_by_wechat_code(self, code: str) -> Dict[str, Any]:
        if not code.strip():
            raise AppError(code="INVALID_INPUT", message="code 不能为空", status_code=400)

        profile = self.wechat_service.code2session(code.strip())
        openid = str(profile["openid"])
        unionid = profile.get("unionid")

        with self.engine.begin() as conn:
            row = conn.execute(
                text(
                    """
                    SELECT id, openid, unionid, nickname, avatar_url, created_at, last_login_at
                    FROM users
                    WHERE openid = :openid
                    LIMIT 1
                    """
                ),
                {"openid": openid},
            ).mappings().first()

            if row is None:
                conn.execute(
                    text(
                        """
                        INSERT INTO users (openid, unionid, nickname, avatar_url, last_login_at)
                        VALUES (:openid, :unionid, :nickname, :avatar_url, NOW())
                        """
                    ),
                    {
                        "openid": openid,
                        "unionid": unionid,
                        "nickname": "微信用户",
                        "avatar_url": "",
                    },
                )
                row = conn.execute(
                    text(
                        """
                        SELECT id, openid, unionid, nickname, avatar_url, created_at, last_login_at
                        FROM users
                        WHERE openid = :openid
                        LIMIT 1
                        """
                    ),
                    {"openid": openid},
                ).mappings().first()
            else:
                conn.execute(
                    text("UPDATE users SET last_login_at = NOW(), unionid = :unionid WHERE id = :user_id"),
                    {"user_id": row["id"], "unionid": unionid},
                )
                row = conn.execute(
                    text(
                        """
                        SELECT id, openid, unionid, nickname, avatar_url, created_at, last_login_at
                        FROM users
                        WHERE id = :user_id
                        LIMIT 1
                        """
                    ),
                    {"user_id": row["id"]},
                ).mappings().first()

        if row is None:
            raise AppError(code="INTERNAL_ERROR", message="创建用户失败", status_code=500)

        user_id = int(row["id"])
        user = self.get_user_by_id(user_id)
        token = self.jwt_service.issue_token(user_id)

        return {
            "access_token": token,
            "expires_in": self.jwt_service.settings.access_token_ttl,
            "user": user,
        }

    def get_user_by_id(self, user_id: int) -> Dict[str, Any]:
        with self.engine.connect() as conn:
            row = conn.execute(
                text(
                    """
                    SELECT id, openid, unionid, nickname, avatar_url, created_at, last_login_at
                    FROM users
                    WHERE id = :user_id
                    LIMIT 1
                    """
                ),
                {"user_id": user_id},
            ).mappings().first()
            if row is None:
                raise AppError(code="USER_NOT_FOUND", message="用户不存在", status_code=404)

            stats_row = conn.execute(
                text(
                    """
                    SELECT
                        COUNT(*) AS total_sessions,
                        COALESCE(ROUND(AVG(accuracy_rate), 2), 0) AS avg_accuracy_rate
                    FROM quiz_sessions
                    WHERE user_id = :user_id AND status = 'completed'
                    """
                ),
                {"user_id": user_id},
            ).mappings().first()

        user = self._serialize_user(row)
        user["stats"] = {
            "total_sessions": int(stats_row["total_sessions"]) if stats_row else 0,
            "avg_accuracy_rate": float(stats_row["avg_accuracy_rate"]) if stats_row else 0.0,
        }
        return user

    def update_user(self, user_id: int, nickname: str | None, avatar_url: str | None) -> Dict[str, Any]:
        if nickname is None and avatar_url is None:
            raise AppError(code="INVALID_INPUT", message="至少提供一个可更新字段", status_code=400)

        updates: Dict[str, Any] = {}
        set_clauses: list[str] = []

        if nickname is not None:
            normalized = nickname.strip()
            if len(normalized) == 0:
                raise AppError(code="INVALID_INPUT", message="昵称不能为空", status_code=400)
            if len(normalized) > 64:
                raise AppError(code="INVALID_INPUT", message="昵称长度不能超过64", status_code=400)
            updates["nickname"] = normalized
            set_clauses.append("nickname = :nickname")

        if avatar_url is not None:
            normalized_avatar = avatar_url.strip()
            if len(normalized_avatar) > 255:
                raise AppError(code="INVALID_INPUT", message="头像地址长度不能超过255", status_code=400)
            updates["avatar_url"] = normalized_avatar
            set_clauses.append("avatar_url = :avatar_url")

        updates["user_id"] = user_id

        with self.engine.begin() as conn:
            affected = conn.execute(
                text(f"UPDATE users SET {', '.join(set_clauses)} WHERE id = :user_id"),
                updates,
            ).rowcount
            if affected == 0:
                raise AppError(code="USER_NOT_FOUND", message="用户不存在", status_code=404)

        return self.get_user_by_id(user_id)

    @staticmethod
    def _serialize_user(row: Any) -> Dict[str, Any]:
        return {
            "id": int(row["id"]),
            "nickname": row.get("nickname") or "微信用户",
            "avatar_url": row.get("avatar_url") or "",
            "created_at": UserService._to_iso(row.get("created_at")),
            "last_login_at": UserService._to_iso(row.get("last_login_at")),
        }

    @staticmethod
    def _to_iso(value: Any) -> str | None:
        if value is None:
            return None
        if isinstance(value, datetime):
            if value.tzinfo is None:
                value = value.replace(tzinfo=timezone.utc)
            return value.isoformat()
        return str(value)
