from __future__ import annotations

from typing import Any, Optional

import httpx


class WeComAPIError(RuntimeError):
    """企业微信接口返回业务错误时抛出。"""

    def __init__(
        self, errcode: int, errmsg: str, raw: Optional[dict[str, Any]] = None
    ) -> None:
        self.errcode = errcode
        self.errmsg = errmsg
        self.raw = raw or {}
        super().__init__(f"WeCom API error: {errcode} - {errmsg}")


class WeComRequestError(RuntimeError):
    """网络请求或响应解析失败时抛出。"""

    def __init__(
        self,
        message: str,
        response: Optional[httpx.Response] = None,
        cause: Optional[BaseException] = None,
    ) -> None:
        self.response = response
        self.cause = cause
        super().__init__(message)
