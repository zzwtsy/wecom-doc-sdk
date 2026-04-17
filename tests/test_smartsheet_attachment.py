from __future__ import annotations

from typing import Any

import pytest

from wecom_doc_sdk import WeComClient
from wecom_doc_sdk.apis.smartsheet_attachment import SmartSheetAttachmentHelper
from wecom_doc_sdk.models.enums import CellValueKeyType
from wecom_doc_sdk.models.records import (
    AddRecordsResponse,
    GetRecordsResponse,
    UpdateRecordsResponse,
)
from wecom_doc_sdk.models.uploads import (
    ShareFileResponse,
    UploadFileRequest,
    UploadFileResponse,
)


def build_attachment_helper(
    client: WeComClient,
    *,
    add_records: Any,
    update_records: Any,
    get_records: Any,
    upload_file_bytes: Any,
) -> SmartSheetAttachmentHelper:
    """构造附件 helper，便于隔离测试。"""

    return SmartSheetAttachmentHelper(
        client,
        add_records=add_records,
        update_records=update_records,
        get_records=get_records,
        upload_file_bytes=upload_file_bytes,
    )


def test_normalize_attachment_values_rejects_non_list() -> None:
    """附件标准化应拒绝非列表值。"""

    with pytest.raises(ValueError, match="附件字段值必须为附件列表"):
        SmartSheetAttachmentHelper._normalize_attachment_values("invalid")


def test_update_record_with_attachment_append_uses_field_title_query(
    client: WeComClient,
) -> None:
    """追加模式在字段标题场景应通过 field_titles 查询现有附件。"""

    captured_get_payload: dict[str, Any] = {}
    captured_update_payload: dict[str, Any] = {}

    def fake_get_records(payload: dict[str, Any]) -> GetRecordsResponse:
        captured_get_payload.update(payload)
        return GetRecordsResponse.model_validate(
            {
                "errcode": 0,
                "errmsg": "ok",
                "records": [{"record_id": "rec-1", "values": {"附件": []}}],
            }
        )

    def fake_update_records(payload: dict[str, Any]) -> UpdateRecordsResponse:
        captured_update_payload.update(payload)
        return UpdateRecordsResponse.model_validate(
            {
                "errcode": 0,
                "errmsg": "ok",
                "records": [{"record_id": "rec-1", "values": {"附件": []}}],
            }
        )

    helper = build_attachment_helper(
        client,
        add_records=lambda payload: payload,
        update_records=fake_update_records,
        get_records=fake_get_records,
        upload_file_bytes=lambda **_: "FILEID",
    )

    response = helper.update_record_with_attachment(
        docid="DOCID",
        sheet_id="sheet-1",
        record_id="rec-1",
        field_key="附件",
        attachments=[{"file_id": "NEW_FILE", "name": "new.txt"}],
        key_type=CellValueKeyType.CELL_VALUE_KEY_TYPE_FIELD_TITLE,
        append=True,
    )

    assert response.records is not None
    assert captured_get_payload["field_titles"] == ["附件"]
    assert "field_ids" not in captured_get_payload
    assert captured_update_payload["records"][0]["values"] == {
        "附件": [{"file_id": "NEW_FILE", "name": "new.txt"}]
    }


def test_upload_file_and_add_attachment_record_includes_share_url(
    client: WeComClient,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """上传文件后开启 share_link 应补充分享链接并写入 add_records。"""

    captured_add_payload: dict[str, Any] = {}

    def fake_add_records(payload: dict[str, Any]) -> AddRecordsResponse:
        captured_add_payload.update(payload)
        return AddRecordsResponse.model_validate(
            {"errcode": 0, "errmsg": "ok", "records": []}
        )

    helper = build_attachment_helper(
        client,
        add_records=fake_add_records,
        update_records=lambda payload: payload,
        get_records=lambda payload: payload,
        upload_file_bytes=lambda **_: "FILEID",
    )

    def fake_upload_file(
        request: UploadFileRequest | dict[str, Any],
    ) -> UploadFileResponse:
        return UploadFileResponse(fileid="FILEID")

    def fake_share_file(request: dict[str, Any]) -> ShareFileResponse:
        assert request == {"fileid": "FILEID"}
        return ShareFileResponse(share_url="https://example.com/share")

    monkeypatch.setattr(client.uploads, "upload_file", fake_upload_file)
    monkeypatch.setattr(client.uploads, "share_file", fake_share_file)

    response = helper.upload_file_and_add_attachment_record(
        docid="DOCID",
        sheet_id="sheet-1",
        field_key="FILE_FIELD_ID",
        upload_request={
            "spaceid": "SPACEID",
            "fatherid": "FOLDERID",
            "file_name": "example.txt",
            "file_base64_content": "BASE64DATA",
        },
        share_link=True,
    )

    assert response.records == []
    assert captured_add_payload == {
        "docid": "DOCID",
        "sheet_id": "sheet-1",
        "key_type": "CELL_VALUE_KEY_TYPE_FIELD_ID",
        "records": [
            {
                "values": {
                    "FILE_FIELD_ID": [
                        {
                            "file_id": "FILEID",
                            "file_url": "https://example.com/share",
                        }
                    ]
                }
            }
        ],
    }


def test_upload_bytes_and_update_attachment_record_builds_default_metadata(
    client: WeComClient,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """基于字节更新附件时应补齐默认附件元数据。"""

    captured_update_payload: dict[str, Any] = {}

    def fake_update_records(payload: dict[str, Any]) -> UpdateRecordsResponse:
        captured_update_payload.update(payload)
        return UpdateRecordsResponse.model_validate(
            {
                "errcode": 0,
                "errmsg": "ok",
                "records": [{"record_id": "rec-1", "values": {"FILE_FIELD_ID": []}}],
            }
        )

    helper = build_attachment_helper(
        client,
        add_records=lambda payload: payload,
        update_records=fake_update_records,
        get_records=lambda payload: payload,
        upload_file_bytes=lambda **_: "FILEID",
    )

    def fake_share_file(request: dict[str, Any]) -> ShareFileResponse:
        return ShareFileResponse(share_url="https://example.com/share")

    monkeypatch.setattr(client.uploads, "share_file", fake_share_file)

    response = helper.upload_bytes_and_update_attachment_record(
        docid="DOCID",
        sheet_id="sheet-1",
        record_id="rec-1",
        field_key="FILE_FIELD_ID",
        file_name="report.pdf",
        file_bytes=b"hello",
    )

    assert response.records is not None
    assert captured_update_payload["records"][0]["values"] == {
        "FILE_FIELD_ID": [
            {
                "file_id": "FILEID",
                "name": "report.pdf",
                "size": 5,
                "doc_type": 2,
                "file_type": "Wedrive",
                "file_ext": "PDF",
                "file_url": "https://example.com/share",
            }
        ]
    }
