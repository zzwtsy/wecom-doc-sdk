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
