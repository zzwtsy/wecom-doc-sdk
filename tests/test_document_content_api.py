from __future__ import annotations

from collections.abc import Callable

import pytest
from pydantic import ValidationError

from wecom_doc_sdk import WeComClient
from wecom_doc_sdk.apis import DocumentContentAPI
from wecom_doc_sdk.models.document_content import (
    BatchUpdateDocumentRequest,
    InsertText,
    Location,
    UpdateRequest,
)


def test_client_mounts_document_content_api(client: WeComClient) -> None:
    """客户端应默认挂载文档内容 API。"""

    assert isinstance(client.document_content, DocumentContentAPI)


def test_get_document_parses_tree_like_payload(
    client: WeComClient,
    bind_request_json: Callable[[dict[str, object]], dict[str, object]],
) -> None:
    """获取文档数据应命中正确路径并保留节点树结构。"""

    captured = bind_request_json(
        {
            "errcode": 0,
            "errmsg": "ok",
            "version": 10,
            "document": {
                "type": "Document",
                "children": [{"type": "Paragraph", "children": [{"type": "Text"}]}],
            },
        },
    )

    response = client.document_content.get({"docid": "DOCID"})

    assert response.ok is True
    assert response.version == 10
    assert captured["path"] == "/cgi-bin/wedoc/document/get"
    assert captured["json"] == {"docid": "DOCID"}
    assert response.document is not None
    assert response.document.type == "Document"


def test_batch_update_serializes_requests_and_version(
    client: WeComClient,
    bind_request_json: Callable[[dict[str, object]], dict[str, object]],
) -> None:
    """批量更新应正确透传 requests 与 version。"""

    captured = bind_request_json({"errcode": 0, "errmsg": "ok"})

    response = client.document_content.batch_update(
        BatchUpdateDocumentRequest(
            docid="DOCID",
            version=11,
            requests=[
                UpdateRequest(
                    insert_text=InsertText(text="hello", location=Location(index=10))
                )
            ],
        )
    )

    assert response.ok is True
    assert captured["path"] == "/cgi-bin/wedoc/document/batch_update"
    assert captured["json"] == {
        "docid": "DOCID",
        "version": 11,
        "requests": [{"insert_text": {"text": "hello", "location": {"index": 10}}}],
    }


def test_batch_update_request_accepts_verison_alias() -> None:
    """请求模型应兼容官方示例中的 `verison` 拼写。"""

    req = BatchUpdateDocumentRequest.model_validate(
        {
            "docid": "DOCID",
            "verison": 12,
            "requests": [{"insert_paragraph": {"location": {"index": 1}}}],
        }
    )
    assert req.version == 12


def test_batch_update_request_requires_exactly_one_operation() -> None:
    """单个更新操作必须且只能包含一个操作字段。"""

    with pytest.raises(ValidationError):
        BatchUpdateDocumentRequest.model_validate(
            {
                "docid": "DOCID",
                "requests": [
                    {
                        "insert_paragraph": {"location": {"index": 1}},
                        "insert_page_break": {"location": {"index": 2}},
                    }
                ],
            }
        )
