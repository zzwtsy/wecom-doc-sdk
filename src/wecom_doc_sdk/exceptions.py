from __future__ import annotations

from typing import Any, Optional

import httpx


class WeComAPIError(RuntimeError):
    """企业微信接口返回业务错误时抛出。

    这类异常表示请求已成功到达企业微信，但接口返回了非零 `errcode`。
    排查时应优先依据 `errcode`，`errmsg` 只作为辅助说明。
    """

    def __init__(
        self, errcode: int, errmsg: str, raw: Optional[dict[str, Any]] = None
    ) -> None:
        self.errcode = errcode
        self.errmsg = errmsg
        # 保留企业微信原始 JSON，便于调用方在日志中定位字段级问题。
        self.raw = raw or {}
        super().__init__(f"WeCom API error: {errcode} - {errmsg}")


class WeComRequestError(RuntimeError):
    """网络请求、HTTP 状态或响应解析失败时抛出。

    这类异常通常发生在企业微信真正返回业务结果之前，适合用来区分：
    - 网络连接异常；
    - HTTP 状态码异常；
    - 返回体不是预期 JSON。
    """

    def __init__(
        self,
        message: str,
        response: Optional[httpx.Response] = None,
        cause: Optional[BaseException] = None,
    ) -> None:
        # 原始响应可帮助排查状态码、响应头或非 JSON 返回体。
        self.response = response
        # 透传底层异常，方便日志或调用方保留完整调用栈。
        self.cause = cause
        super().__init__(message)
