from __future__ import annotations

from typing import Callable

import pytest
from pydantic import ValidationError

from wecom_doc_sdk import WeComClient
from wecom_doc_sdk.models.uploads import UploadFileRequest, UploadImageRequest


def test_upload_image_serializes_model_request(
    client: WeComClient,
    bind_request_json: Callable[[dict[str, object]], dict[str, object]],
) -> None:
    """上传图片应命中正确路径并序列化请求。"""

    captured = bind_request_json(
        {
            "errcode": 0,
            "errmsg": "ok",
            "url": "https://example.com/image.png",
            "height": 100,
            "width": 120,
            "size": 1024,
        }
    )

    response = client.uploads.upload_image(
        UploadImageRequest(docid="DOCID", base64_content="BASE64DATA")
    )

    assert response.url == "https://example.com/image.png"
    assert response.height == 100
    assert response.width == 120
    assert response.size == 1024
    assert captured["path"] == "/cgi-bin/wedoc/image_upload"
    assert captured["json"] == {"docid": "DOCID", "base64_content": "BASE64DATA"}


def test_upload_image_accepts_dict_request(
    client: WeComClient,
    bind_request_json: Callable[[dict[str, object]], dict[str, object]],
) -> None:
    """上传图片应支持 dict 入参并正确透传字段。"""
    captured = bind_request_json(
        {
            "errcode": 0,
            "errmsg": "ok",
            "url": "https://example.com/image.png",
            "height": 100,
            "width": 120,
            "size": 1024,
        }
    )

    response = client.uploads.upload_image(
        {"docid": "DOCID", "base64_content": "BASE64DATA"}
    )

    assert response.url == "https://example.com/image.png"
    assert response.height == 100
    assert response.width == 120
    assert response.size == 1024
    assert captured["path"] == "/cgi-bin/wedoc/image_upload"
    assert captured["json"] == {"docid": "DOCID", "base64_content": "BASE64DATA"}


def test_upload_file_serializes_model_request(
    client: WeComClient,
    bind_request_json: Callable[[dict[str, object]], dict[str, object]],
) -> None:
    """上传微盘文件应命中正确路径并序列化请求。"""

    captured = bind_request_json({"errcode": 0, "errmsg": "ok", "fileid": "FILEID"})

    response = client.uploads.upload_file(
        {
            "spaceid": "SPACEID",
            "fatherid": "FOLDERID",
            "file_name": "example.txt",
            "file_base64_content": "BASE64DATA",
        }
    )

    assert response.fileid == "FILEID"
    assert captured["path"] == "/cgi-bin/wedrive/file_upload"
    assert captured["json"] == {
        "spaceid": "SPACEID",
        "fatherid": "FOLDERID",
        "file_name": "example.txt",
        "file_base64_content": "BASE64DATA",
    }


def test_share_file_serializes_dict_request(
    client: WeComClient,
    bind_request_json: Callable[[dict[str, object]], dict[str, object]],
) -> None:
    """获取微盘文件分享链接应命中正确路径并正确序列化请求。"""

    captured = bind_request_json(
        {"errcode": 0, "errmsg": "ok", "share_url": "https://example.com/share"}
    )

    response = client.uploads.share_file({"fileid": "FILEID"})

    assert response.share_url == "https://example.com/share"
    assert captured["path"] == "/cgi-bin/wedrive/file_share"
    assert captured["json"] == {"fileid": "FILEID"}


@pytest.mark.parametrize(
    "payload",
    [
        {
            "spaceid": "SPACEID",
            "file_name": "example.txt",
            "file_base64_content": "BASE64DATA",
        },
        {
            "fatherid": "FOLDERID",
            "file_name": "example.txt",
            "file_base64_content": "BASE64DATA",
        },
        {
            "file_name": "example.txt",
            "file_base64_content": "BASE64DATA",
        },
        {
            "spaceid": "SPACEID",
            "fatherid": "FOLDERID",
            "selected_ticket": "TICKET",
            "file_name": "example.txt",
            "file_base64_content": "BASE64DATA",
        },
    ],
)
def test_upload_file_request_rejects_invalid_target_group(
    payload: dict[str, str],
) -> None:
    """上传文件请求应严格校验目标参数组合。"""

    with pytest.raises(ValidationError):
        UploadFileRequest.model_validate(payload)


def test_upload_file_request_accepts_space_and_father_group() -> None:
    """上传文件请求在 spaceid 与 fatherid 同时提供时应校验通过。"""

    request = UploadFileRequest.model_validate(
        {
            "spaceid": "SPACEID",
            "fatherid": "FOLDERID",
            "file_name": "example.txt",
            "file_base64_content": "BASE64DATA",
        }
    )
    assert request.spaceid == "SPACEID"
    assert request.fatherid == "FOLDERID"


def test_upload_file_request_accepts_selected_ticket_group() -> None:
    """上传文件请求在 selected_ticket 模式下应校验通过。"""

    request = UploadFileRequest.model_validate(
        {
            "selected_ticket": "TICKET",
            "file_name": "example.txt",
            "file_base64_content": "BASE64DATA",
        }
    )
    assert request.selected_ticket == "TICKET"
