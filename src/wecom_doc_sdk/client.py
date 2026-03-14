from __future__ import annotations

import threading
import time
from typing import Any, Dict, Optional

import httpx
from pydantic import BaseModel

from .exceptions import WeComAPIError, WeComRequestError


class AccessTokenResponse(BaseModel):
    errcode: int = 0
    errmsg: str = ""
    access_token: Optional[str] = None
    expires_in: Optional[int] = None


class AccessTokenProvider:
    """access_token 获取与缓存。

    说明：
    - 内部会做简单缓存与提前刷新（默认提前 120 秒）。
    - 仅用于企业微信自建应用的 corpid/secret 换取 token 场景。
    """

    def __init__(
        self,
        corp_id: str,
        corp_secret: str,
        *,
        base_url: str = "https://qyapi.weixin.qq.com",
        timeout: float = 10.0,
        refresh_buffer: int = 120,
        http_client: Optional[httpx.Client] = None,
    ) -> None:
        self._corp_id = corp_id
        self._corp_secret = corp_secret
        self._refresh_buffer = refresh_buffer
        self._lock = threading.Lock()
        self._token: Optional[str] = None
        self._expire_at: float = 0.0
        self._owns_client = http_client is None
        self._client = http_client or httpx.Client(base_url=base_url, timeout=timeout)

    def close(self) -> None:
        if self._owns_client:
            self._client.close()

    def get(self) -> str:
        """获取可用的 access_token。"""

        if self._token and time.time() < self._expire_at - self._refresh_buffer:
            return self._token
        # 多线程场景下仅允许一个线程刷新
        with self._lock:
            if self._token and time.time() < self._expire_at - self._refresh_buffer:
                return self._token
            self._refresh_token()
            if not self._token:
                raise WeComRequestError("获取 access_token 失败：返回为空")
            return self._token

    def _refresh_token(self) -> None:
        try:
            resp = self._client.get(
                "/cgi-bin/gettoken",
                params={"corpid": self._corp_id, "corpsecret": self._corp_secret},
            )
        except httpx.HTTPError as exc:
            raise WeComRequestError(
                "获取 access_token 失败：网络异常", cause=exc
            ) from exc

        if resp.status_code >= 400:
            raise WeComRequestError(
                "获取 access_token 失败：HTTP 状态异常", response=resp
            )

        try:
            payload = resp.json()
        except ValueError as exc:
            raise WeComRequestError(
                "获取 access_token 失败：响应不是 JSON", response=resp, cause=exc
            ) from exc

        data = AccessTokenResponse.model_validate(payload)
        if data.errcode != 0:
            raise WeComAPIError(data.errcode, data.errmsg, payload)

        self._token = data.access_token
        expires_in = int(data.expires_in or 0)
        # 记录过期时间（秒级）
        self._expire_at = time.time() + expires_in


class WeComClient:
    """企业微信文档 SDK 客户端（同步版）。"""

    def __init__(
        self,
        corp_id: str,
        corp_secret: str,
        *,
        base_url: str = "https://qyapi.weixin.qq.com",
        timeout: float = 10.0,
    ) -> None:
        self._http = httpx.Client(base_url=base_url, timeout=timeout)
        # 复用 httpx.Client 以减少连接开销
        self._token_provider = AccessTokenProvider(
            corp_id,
            corp_secret,
            base_url=base_url,
            timeout=timeout,
            http_client=self._http,
        )
        # 延迟导入避免循环依赖
        from .apis.smartsheet import SmartSheetAPI

        self.smartsheet = SmartSheetAPI(self)

    def close(self) -> None:
        """关闭底层 HTTP 连接。"""

        self._http.close()

    def __enter__(self) -> "WeComClient":
        return self

    def __exit__(self, exc_type, exc, tb) -> None:  # noqa: D401 - 遵循上下文管理协议
        self.close()

    def request_json(
        self,
        method: str,
        path: str,
        *,
        params: Optional[Dict[str, Any]] = None,
        json: Optional[Dict[str, Any]] = None,
    ) -> Dict[str, Any]:
        """统一请求入口，自动注入 access_token 并处理错误。"""

        token = self._token_provider.get()
        request_params = dict(params or {})
        request_params["access_token"] = token

        try:
            response = self._http.request(
                method, path, params=request_params, json=json
            )
        except httpx.HTTPError as exc:
            raise WeComRequestError("请求企业微信接口失败", cause=exc) from exc

        if response.status_code >= 400:
            raise WeComRequestError(
                "请求企业微信接口失败：HTTP 状态异常", response=response
            )

        try:
            payload = response.json()
        except ValueError as exc:
            raise WeComRequestError(
                "响应解析失败：不是 JSON", response=response, cause=exc
            ) from exc

        if isinstance(payload, dict) and payload.get("errcode", 0) != 0:
            raise WeComAPIError(
                int(payload.get("errcode", -1)), str(payload.get("errmsg", "")), payload
            )

        return payload

    @staticmethod
    def dump_model(model: BaseModel) -> Dict[str, Any]:
        """统一的模型序列化，便于后续扩展配置。"""

        return model.model_dump(by_alias=True, exclude_none=True)
