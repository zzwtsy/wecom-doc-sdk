from __future__ import annotations

from collections.abc import Callable, Iterator
from typing import Any

import pytest

from wecom_doc_sdk import WeComClient


@pytest.fixture
def client() -> Iterator[WeComClient]:
    """提供一个可关闭的 SDK 客户端实例。"""

    sdk_client = WeComClient("corp-id", "corp-secret")
    try:
        yield sdk_client
    finally:
        sdk_client.close()


@pytest.fixture
def bind_request_json(client: WeComClient) -> Callable[[dict[str, Any]], dict[str, Any]]:
    """替换 request_json 并返回捕获的调用明细。"""

    def _bind(payload: dict[str, Any]) -> dict[str, Any]:
        captured: dict[str, Any] = {}

        def fake_request_json(
            method: str,
            path: str,
            *,
            params: dict[str, Any] | None = None,
            json: dict[str, Any] | None = None,
        ) -> dict[str, Any]:
            captured["method"] = method
            captured["path"] = path
            captured["params"] = params
            captured["json"] = json
            return payload

        client.request_json = fake_request_json  # type: ignore[method-assign]
        return captured

    return _bind
