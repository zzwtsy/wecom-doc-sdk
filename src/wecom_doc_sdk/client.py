from __future__ import annotations

import threading
import time
from typing import Any, Dict, Optional

import httpx
from pydantic import BaseModel

from .exceptions import WeComAPIError, WeComRequestError


class AccessTokenResponse(BaseModel):
    """`/cgi-bin/gettoken` 接口响应。

    企业微信会返回凭证本身及其秒级有效期。SDK 会基于该结构做本地缓存，
    并在凭证过期前提前刷新，避免业务请求在边界时刻拿到失效 token。
    """

    errcode: int = 0
    errmsg: str = ""
    access_token: Optional[str] = None
    expires_in: Optional[int] = None


class AccessTokenProvider:
    """access_token 获取与缓存。

    说明：
    - 内部会做简单缓存与提前刷新（默认提前 120 秒）。
    - 仅用于企业微信自建应用的 corpid/secret 换取 token 场景。
    - 企业微信官方文档要求开发者在服务端缓存 token，并在失效时重新获取。
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
        """关闭内部持有的 HTTP 客户端。

        当调用方复用了外部传入的 `httpx.Client` 时，由调用方自己负责关闭。
        """

        if self._owns_client:
            self._client.close()

    def get(self) -> str:
        """获取当前可用的 access_token。

        优先返回缓存中的 token；如果缓存不存在或即将过期，则在锁保护下刷新。
        这样可以避免多线程环境下重复请求 `/cgi-bin/gettoken`。
        """

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
        """调用企业微信 `gettoken` 接口刷新缓存中的 access_token。"""

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
        # 企业微信官方文档明确要求以 errcode 判断是否成功，errmsg 仅用于辅助排障。
        if data.errcode != 0:
            raise WeComAPIError(data.errcode, data.errmsg, payload)

        self._token = data.access_token
        expires_in = int(data.expires_in or 0)
        # 记录过期时间（秒级）；后续读取时会结合 refresh_buffer 提前刷新。
        self._expire_at = time.time() + expires_in


class WeComClient:
    """企业微信文档 SDK 客户端（同步版）。

    负责统一管理底层 HTTP 连接、access_token 获取逻辑，以及各业务 API 模块。
    当前默认挂载文档管理接口 `documents`、文档内容接口 `document_content`、
    智能表格内容接口 `smartsheet`，以及设置文档权限接口 `permissions`。
    """

    def __init__(
        self,
        corp_id: str,
        corp_secret: str,
        *,
        base_url: str = "https://qyapi.weixin.qq.com",
        timeout: float = 10.0,
    ) -> None:
        self._http = httpx.Client(base_url=base_url, timeout=timeout)
        # 复用 httpx.Client 以减少连接开销，并与 token 获取共用一套超时配置。
        self._token_provider = AccessTokenProvider(
            corp_id,
            corp_secret,
            base_url=base_url,
            timeout=timeout,
            http_client=self._http,
        )
        # 延迟导入避免循环依赖
        from .apis.document_content import DocumentContentAPI
        from .apis.documents import DocumentsAPI
        from .apis.permissions import PermissionsAPI
        from .apis.smartsheet import SmartSheetAPI
        from .apis.uploads import UploadsAPI

        self.documents = DocumentsAPI(self)
        self.document_content = DocumentContentAPI(self)
        self.permissions = PermissionsAPI(self)
        self.smartsheet = SmartSheetAPI(self)
        self.uploads = UploadsAPI(self)

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
        """统一发送企业微信 JSON 请求。

        该方法会自动注入 `access_token`，并统一处理三类错误：
        - 网络层或 HTTP 状态异常；
        - 响应体不是合法 JSON；
        - 企业微信返回 `errcode != 0` 的业务错误。
        """

        token = self._token_provider.get()
        request_params = dict(params or {})
        # 企业微信大多数服务端接口都要求将 access_token 放在查询参数中。
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

        # 根据企业微信全局错误码文档，必须优先使用 errcode 判断业务是否成功。
        if isinstance(payload, dict) and payload.get("errcode", 0) != 0:
            raise WeComAPIError(
                int(payload.get("errcode", -1)), str(payload.get("errmsg", "")), payload
            )

        return payload

    def request_form(
        self,
        method: str,
        path: str,
        *,
        params: Optional[Dict[str, Any]] = None,
        data: Optional[Dict[str, Any]] = None,
        files: Optional[Dict[str, Any]] = None,
    ) -> Dict[str, Any]:
        """统一发送企业微信表单/文件上传请求。"""

        token = self._token_provider.get()
        request_params = dict(params or {})
        request_params["access_token"] = token

        try:
            response = self._http.request(
                method,
                path,
                params=request_params,
                data=data,
                files=files,
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
        """统一序列化 Pydantic 模型。

        默认使用字段别名并忽略空值，避免把未填写的可选字段透传给企业微信接口。
        """

        return model.model_dump(by_alias=True, exclude_none=True)
