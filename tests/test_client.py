from __future__ import annotations

from typing import Any

import httpx
import pytest
from pydantic import BaseModel, Field

from wecom_doc_sdk.client import AccessTokenProvider, WeComClient
from wecom_doc_sdk.exceptions import WeComAPIError, WeComRequestError


def _json_response(
    payload: dict[str, Any], status_code: int = 200, path: str = "/mock"
) -> httpx.Response:
    request = httpx.Request("GET", f"https://qyapi.weixin.qq.com{path}")
    return httpx.Response(status_code, json=payload, request=request)


def test_access_token_provider_reuses_cached_token() -> None:
    """token 在有效期内应直接命中缓存，不重复请求远端。"""

    class DummyHTTPClient:
        def __init__(self) -> None:
            self.calls = 0

        def get(self, path: str, *, params: dict[str, Any]) -> httpx.Response:
            self.calls += 1
            assert path == "/cgi-bin/gettoken"
            assert "corpid" in params
            assert "corpsecret" in params
            return _json_response(
                {"errcode": 0, "errmsg": "ok", "access_token": "TOKEN", "expires_in": 7200}
            )

        def close(self) -> None:
            return None

    http_client = DummyHTTPClient()
    provider = AccessTokenProvider("corp-id", "corp-secret", http_client=http_client)

    first = provider.get()
    second = provider.get()

    assert first == "TOKEN"
    assert second == "TOKEN"
    assert http_client.calls == 1


@pytest.mark.parametrize(
    ("factory", "expected_exception"),
    [
        (
            lambda: (_ for _ in ()).throw(
                httpx.ConnectError("boom", request=httpx.Request("GET", "https://qyapi.weixin.qq.com/cgi-bin/gettoken"))
            ),
            WeComRequestError,
        ),
        (lambda: _json_response({}, status_code=500), WeComRequestError),
        (
            lambda: httpx.Response(
                200,
                content=b"not-json",
                request=httpx.Request("GET", "https://qyapi.weixin.qq.com/cgi-bin/gettoken"),
            ),
            WeComRequestError,
        ),
        (lambda: _json_response({"errcode": 40013, "errmsg": "invalid"}), WeComAPIError),
        (
            lambda: _json_response({"errcode": 0, "errmsg": "ok", "expires_in": 7200}),
            WeComRequestError,
        ),
    ],
)
def test_access_token_provider_error_mapping(
    factory: Any, expected_exception: type[Exception]
) -> None:
    """token 刷新各类失败应映射为统一异常。"""

    class DummyHTTPClient:
        def get(self, path: str, *, params: dict[str, Any]) -> httpx.Response:
            result = factory()
            if isinstance(result, httpx.Response):
                return result
            raise AssertionError("factory must return httpx.Response")

        def close(self) -> None:
            return None

    provider = AccessTokenProvider("corp-id", "corp-secret", http_client=DummyHTTPClient())

    with pytest.raises(expected_exception):
        provider.get()


def test_request_json_injects_access_token_and_preserves_params() -> None:
    """请求应自动注入 access_token 并保留原参数。"""

    client = WeComClient("corp-id", "corp-secret")
    client._token_provider.get = lambda: "ACCESS_TOKEN"  # type: ignore[method-assign]

    captured: dict[str, Any] = {}

    def fake_request(
        method: str,
        path: str,
        *,
        params: dict[str, Any] | None = None,
        json: dict[str, Any] | None = None,
    ) -> httpx.Response:
        captured["method"] = method
        captured["path"] = path
        captured["params"] = params
        captured["json"] = json
        return _json_response({"errcode": 0, "errmsg": "ok", "value": 1}, path=path)

    client._http.request = fake_request  # type: ignore[method-assign]
    payload = client.request_json(
        "POST", "/cgi-bin/wedoc/get_doc_base_info", params={"lang": "zh_CN"}, json={"docid": "D"}
    )

    assert payload["value"] == 1
    assert captured["method"] == "POST"
    assert captured["path"] == "/cgi-bin/wedoc/get_doc_base_info"
    assert captured["json"] == {"docid": "D"}
    assert captured["params"] == {"lang": "zh_CN", "access_token": "ACCESS_TOKEN"}
    client.close()


@pytest.mark.parametrize(
    ("factory", "expected_exception"),
    [
        (
            lambda: (_ for _ in ()).throw(
                httpx.ConnectError("boom", request=httpx.Request("POST", "https://qyapi.weixin.qq.com/mock"))
            ),
            WeComRequestError,
        ),
        (lambda: _json_response({}, status_code=502), WeComRequestError),
        (
            lambda: httpx.Response(
                200,
                content=b"not-json",
                request=httpx.Request("POST", "https://qyapi.weixin.qq.com/mock"),
            ),
            WeComRequestError,
        ),
        (lambda: _json_response({"errcode": 48001, "errmsg": "forbidden"}), WeComAPIError),
    ],
)
def test_request_json_error_mapping(
    factory: Any, expected_exception: type[Exception]
) -> None:
    """request_json 应统一映射网络、协议与业务异常。"""

    client = WeComClient("corp-id", "corp-secret")
    client._token_provider.get = lambda: "ACCESS_TOKEN"  # type: ignore[method-assign]

    def fake_request(
        method: str,
        path: str,
        *,
        params: dict[str, Any] | None = None,
        json: dict[str, Any] | None = None,
    ) -> httpx.Response:
        result = factory()
        if isinstance(result, httpx.Response):
            return result
        raise AssertionError("factory must return httpx.Response")

    client._http.request = fake_request  # type: ignore[method-assign]

    with pytest.raises(expected_exception):
        client.request_json("POST", "/mock")
    client.close()


def test_dump_model_uses_alias_and_excludes_none() -> None:
    """模型序列化应使用别名并剔除空值。"""

    class DemoModel(BaseModel):
        doc_id: str = Field(alias="docid")
        optional_text: str | None = None

    payload = WeComClient.dump_model(DemoModel(docid="DOCID"))

    assert payload == {"docid": "DOCID"}


def test_access_token_provider_close_respects_ownership() -> None:
    """provider 仅应关闭自己创建的 http client。"""

    class DummyHTTPClient:
        def __init__(self) -> None:
            self.closed = False

        def get(self, path: str, *, params: dict[str, Any]) -> httpx.Response:
            return _json_response(
                {"errcode": 0, "errmsg": "ok", "access_token": "TOKEN", "expires_in": 7200}
            )

        def close(self) -> None:
            self.closed = True

    external_client = DummyHTTPClient()
    provider = AccessTokenProvider("corp-id", "corp-secret", http_client=external_client)
    provider.close()
    assert external_client.closed is False


def test_wecom_client_context_manager_closes_http_client() -> None:
    """上下文管理器退出时应关闭底层 http client。"""

    client = WeComClient("corp-id", "corp-secret")
    closed = {"value": False}

    def fake_close() -> None:
        closed["value"] = True

    client._http.close = fake_close  # type: ignore[method-assign]

    with client as managed:
        assert managed is client

    assert closed["value"] is True


def test_access_token_provider_closes_internal_http_client() -> None:
    """provider 持有内部 client 时应在 close 时关闭连接。"""

    class DummyHTTPClient:
        def __init__(self) -> None:
            self.closed = False

        def close(self) -> None:
            self.closed = True

    provider = AccessTokenProvider("corp-id", "corp-secret", http_client=DummyHTTPClient())
    provider._owns_client = True  # type: ignore[assignment]
    provider.close()
    assert provider._client.closed is True  # type: ignore[attr-defined]


def test_access_token_provider_returns_cached_token_inside_lock() -> None:
    """进入锁后若已有可用 token，应直接返回而不刷新。"""

    class DummyHTTPClient:
        def get(self, path: str, *, params: dict[str, Any]) -> httpx.Response:
            raise AssertionError("should not refresh token")

        def close(self) -> None:
            return None

    class TokenInjectLock:
        def __init__(self, provider: AccessTokenProvider) -> None:
            self.provider = provider

        def __enter__(self) -> None:
            self.provider._token = "LOCK_TOKEN"
            self.provider._expire_at = 9999999999.0
            return None

        def __exit__(self, exc_type, exc, tb) -> None:
            return None

    provider = AccessTokenProvider("corp-id", "corp-secret", http_client=DummyHTTPClient())
    provider._lock = TokenInjectLock(provider)  # type: ignore[assignment]

    token = provider.get()
    assert token == "LOCK_TOKEN"
