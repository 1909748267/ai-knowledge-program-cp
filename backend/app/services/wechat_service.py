from typing import Any, Dict

import httpx

from app.config import get_settings
from app.errors import AppError


class WechatService:
    def __init__(self) -> None:
        self.settings = get_settings()

    def code2session(self, code: str) -> Dict[str, Any]:
        if not self.settings.wechat_appid or not self.settings.wechat_secret:
            raise AppError(code="WECHAT_CONFIG_MISSING", message="未配置微信登录参数", status_code=500)

        params = {
            "appid": self.settings.wechat_appid,
            "secret": self.settings.wechat_secret,
            "js_code": code,
            "grant_type": "authorization_code",
        }

        try:
            response = httpx.get(
                "https://api.weixin.qq.com/sns/jscode2session",
                params=params,
                timeout=10,
            )
            data = response.json()
        except Exception as exc:
            raise AppError(code="WECHAT_API_ERROR", message="微信登录服务异常", status_code=502) from exc

        if not isinstance(data, dict):
            raise AppError(code="WECHAT_API_ERROR", message="微信登录返回格式异常", status_code=502)

        if data.get("errcode"):
            raise AppError(
                code="WECHAT_LOGIN_FAILED",
                message=f"微信登录失败: {data.get('errmsg', 'unknown error')}",
                status_code=400,
            )

        openid = data.get("openid")
        session_key = data.get("session_key")
        if not openid or not session_key:
            raise AppError(code="WECHAT_LOGIN_FAILED", message="微信登录凭证无效", status_code=400)

        return data
