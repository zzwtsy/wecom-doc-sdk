from __future__ import annotations

from collections.abc import Callable

import pytest
from pydantic import ValidationError

from wecom_doc_sdk import WeComClient
from wecom_doc_sdk.apis import DocumentsAPI
from wecom_doc_sdk.models.documents import CreateDocRequest, GetDocBaseInfoRequest
from wecom_doc_sdk.models.enums import DocType


def test_client_mounts_documents_api(client: WeComClient) -> None:
    """客户端应默认挂载文档管理 API。"""

    assert isinstance(client.documents, DocumentsAPI)


def test_create_doc_serializes_model_request(
    client: WeComClient,
    bind_request_json: Callable[[dict[str, object]], dict[str, object]],
) -> None:
    """新建文档应命中正确路径并序列化请求体。"""

    captured = bind_request_json(
        {
            "errcode": 0,
            "errmsg": "ok",
            "url": "https://doc.weixin.qq.com/abc",
            "docid": "DOCID",
        },
    )

    response = client.documents.create_doc(
        CreateDocRequest(
            doc_type=DocType.SMARTSHEET,
            doc_name="智能表",
            admin_users=["zhangsan"],
        )
    )

    assert response.ok is True
    assert response.docid == "DOCID"
    assert captured["method"] == "POST"
    assert captured["path"] == "/cgi-bin/wedoc/create_doc"
    assert captured["json"] == {
        "doc_type": 10,
        "doc_name": "智能表",
        "admin_users": ["zhangsan"],
    }


def test_get_doc_base_info_parses_nested_response(
    client: WeComClient,
    bind_request_json: Callable[[dict[str, object]], dict[str, object]],
) -> None:
    """获取文档基础信息应解析 doc_base_info。"""

    captured = bind_request_json(
        {
            "errcode": 0,
            "errmsg": "ok",
            "doc_base_info": {
                "docid": "DOCID",
                "doc_name": "名称",
                "create_time": 1717071093,
                "modify_time": 1717071199,
                "doc_type": 3,
            },
        },
    )

    response = client.documents.get_doc_base_info(GetDocBaseInfoRequest(docid="DOCID"))

    assert captured["path"] == "/cgi-bin/wedoc/get_doc_base_info"
    assert captured["json"] == {"docid": "DOCID"}
    assert response.doc_base_info is not None
    assert response.doc_base_info.doc_name == "名称"
    assert response.doc_base_info.doc_type == 3


def test_doc_share_delete_and_rename_accept_dict_request(
    client: WeComClient,
    bind_request_json: Callable[[dict[str, object]], dict[str, object]],
) -> None:
    """分享、删除和重命名接口应支持 dict 请求。"""

    captured = bind_request_json({"errcode": 0, "errmsg": "ok", "share_url": "URL"})
    share_response = client.documents.doc_share({"docid": "DOCID"})
    assert share_response.share_url == "URL"
    assert captured["path"] == "/cgi-bin/wedoc/doc_share"
    assert captured["json"] == {"docid": "DOCID"}

    captured = bind_request_json({"errcode": 0, "errmsg": "ok"})
    delete_response = client.documents.delete_doc({"formid": "FORMID"})
    assert delete_response.ok is True
    assert captured["path"] == "/cgi-bin/wedoc/del_doc"
    assert captured["json"] == {"formid": "FORMID"}

    captured = bind_request_json({"errcode": 0, "errmsg": "ok"})
    rename_response = client.documents.rename_doc(
        {"docid": "DOCID", "new_name": "新名字"}
    )
    assert rename_response.ok is True
    assert captured["path"] == "/cgi-bin/wedoc/rename_doc"
    assert captured["json"] == {"docid": "DOCID", "new_name": "新名字"}


@pytest.mark.parametrize(
    "payload",
    [
        {"docid": "DOCID", "formid": "FORMID"},
        {},
    ],
)
def test_docid_formid_requires_exactly_one(payload: dict[str, str]) -> None:
    """分享/删除/重命名请求中的 docid 与 formid 必须二选一。"""

    from wecom_doc_sdk.models.documents import (
        DeleteDocRequest,
        DocShareRequest,
        RenameDocRequest,
    )

    with pytest.raises(ValidationError):
        DocShareRequest.model_validate(payload)

    with pytest.raises(ValidationError):
        DeleteDocRequest.model_validate(payload)

    with pytest.raises(ValidationError):
        RenameDocRequest.model_validate({**payload, "new_name": "name"})
