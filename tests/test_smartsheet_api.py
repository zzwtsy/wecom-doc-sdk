from __future__ import annotations

from collections.abc import Callable

import pytest
from pydantic import ValidationError

from wecom_doc_sdk import WeComClient
from wecom_doc_sdk.exceptions import WeComRequestError
from wecom_doc_sdk.models.fields import AddField, AddFieldsRequest, FieldType
from wecom_doc_sdk.models.groups import AddFieldGroupRequest, FieldGroupChild
from wecom_doc_sdk.models.sheets import AddSheetProperties, AddSheetRequest
from wecom_doc_sdk.models.uploads import ShareFileResponse, UploadFileResponse
from wecom_doc_sdk.models.views import AddViewRequest, ViewType


def test_add_sheet_serializes_model_request(
    client: WeComClient,
    bind_request_json: Callable[[dict[str, object]], dict[str, object]],
) -> None:
    """新增子表应命中正确路径并序列化请求。"""

    captured = bind_request_json(
        {"errcode": 0, "errmsg": "ok", "properties": {"sheet_id": "sheet-1"}}
    )

    response = client.smartsheet.add_sheet(
        AddSheetRequest(
            docid="DOCID",
            properties=AddSheetProperties(title="迭代计划", index=1),
        )
    )

    assert response.properties is not None
    assert response.properties.sheet_id == "sheet-1"
    assert captured["path"] == "/cgi-bin/wedoc/smartsheet/add_sheet"
    assert captured["json"] == {
        "docid": "DOCID",
        "properties": {"title": "迭代计划", "index": 1},
    }


def test_add_view_accepts_dict_request(
    client: WeComClient,
    bind_request_json: Callable[[dict[str, object]], dict[str, object]],
) -> None:
    """新增视图应支持 dict 入参并正确透传字段。"""

    captured = bind_request_json(
        {
            "errcode": 0,
            "errmsg": "ok",
            "view": {
                "view_id": "view-1",
                "view_title": "全部任务",
                "view_type": ViewType.VIEW_TYPE_GRID.value,
            },
        },
    )

    response = client.smartsheet.add_view(
        {
            "docid": "DOCID",
            "sheet_id": "sheet-1",
            "view_title": "全部任务",
            "view_type": ViewType.VIEW_TYPE_GRID.value,
        }
    )

    assert response.view is not None
    assert response.view.view_id == "view-1"
    assert captured["path"] == "/cgi-bin/wedoc/smartsheet/add_view"
    assert captured["json"] == {
        "docid": "DOCID",
        "sheet_id": "sheet-1",
        "view_title": "全部任务",
        "view_type": ViewType.VIEW_TYPE_GRID.value,
    }


def test_add_fields_serializes_nested_field_definition(
    client: WeComClient,
    bind_request_json: Callable[[dict[str, object]], dict[str, object]],
) -> None:
    """新增字段应正确序列化字段定义。"""

    captured = bind_request_json(
        {
            "errcode": 0,
            "errmsg": "ok",
            "fields": [
                {
                    "field_id": "field-1",
                    "field_title": "任务名",
                    "field_type": FieldType.FIELD_TYPE_TEXT.value,
                }
            ],
        },
    )

    response = client.smartsheet.add_fields(
        {
            "docid": "DOCID",
            "sheet_id": "sheet-1",
            "fields": [
                {
                    "field_title": "任务名",
                    "field_type": FieldType.FIELD_TYPE_TEXT.value,
                }
            ],
        }
    )

    assert response.fields is not None
    assert response.fields[0].field_id == "field-1"
    assert captured["path"] == "/cgi-bin/wedoc/smartsheet/add_fields"
    assert captured["json"] == {
        "docid": "DOCID",
        "sheet_id": "sheet-1",
        "fields": [
            {
                "field_title": "任务名",
                "field_type": FieldType.FIELD_TYPE_TEXT.value,
            }
        ],
    }


def test_add_records_with_attachment_builds_record_values(
    client: WeComClient,
    bind_request_json: Callable[[dict[str, object]], dict[str, object]],
) -> None:
    """新增附件记录应构造正确的 values 结构并调用 add_records 接口。"""

    captured = bind_request_json({"errcode": 0, "errmsg": "ok", "records": []})

    response = client.smartsheet.add_records_with_attachment(
        docid="DOCID",
        sheet_id="sheet-1",
        field_key="FILE_FIELD_ID",
        attachments=[
            {
                "doc_type": 2,
                "file_ext": "SMARTSHEET",
                "file_id": "FILEID",
                "file_type": "70",
                "file_url": "https://doc.weixin.qq.com/smartsheet/xxx",
                "name": "智能表格",
                "size": 3267,
            }
        ],
    )

    assert response.records == []
    assert captured["path"] == "/cgi-bin/wedoc/smartsheet/add_records"
    assert captured["json"] == {
        "docid": "DOCID",
        "sheet_id": "sheet-1",
        "key_type": "CELL_VALUE_KEY_TYPE_FIELD_ID",
        "records": [
            {
                "values": {
                    "FILE_FIELD_ID": [
                        {
                            "doc_type": 2,
                            "file_ext": "SMARTSHEET",
                            "file_id": "FILEID",
                            "file_type": "70",
                            "file_url": "https://doc.weixin.qq.com/smartsheet/xxx",
                            "name": "智能表格",
                            "size": 3267,
                        }
                    ]
                }
            }
        ],
    }


def test_upload_file_and_add_attachment_record(
    client: WeComClient,
    bind_request_json: Callable[[dict[str, object]], dict[str, object]],
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """上传文件后应将 file_id 写入附件字段并调用 add_records。"""

    captured = bind_request_json({"errcode": 0, "errmsg": "ok", "records": []})

    def fake_upload_file(request: dict[str, object]) -> UploadFileResponse:
        return UploadFileResponse(fileid="FILEID")

    monkeypatch.setattr(client.uploads, "upload_file", fake_upload_file)

    response = client.smartsheet.upload_file_and_add_attachment_record(
        docid="DOCID",
        sheet_id="sheet-1",
        field_key="FILE_FIELD_ID",
        upload_request={
            "spaceid": "SPACEID",
            "fatherid": "FOLDERID",
            "file_name": "example.txt",
            "file_base64_content": "BASE64DATA",
        },
        attachment_metadata={"name": "example.txt", "size": 1024},
    )

    assert response.records == []
    assert captured["path"] == "/cgi-bin/wedoc/smartsheet/add_records"
    assert captured["json"] == {
        "docid": "DOCID",
        "sheet_id": "sheet-1",
        "key_type": "CELL_VALUE_KEY_TYPE_FIELD_ID",
        "records": [
            {
                "values": {
                    "FILE_FIELD_ID": [
                        {
                            "file_id": "FILEID",
                            "name": "example.txt",
                            "size": 1024,
                        }
                    ]
                }
            }
        ],
    }


def test_upload_file_and_add_attachment_record_raises_when_fileid_missing(
    client: WeComClient,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """上传成功响应缺少 fileid 时应直接抛出请求异常。"""

    def fake_upload_file(request: dict[str, object]) -> UploadFileResponse:
        return UploadFileResponse(fileid=None)

    monkeypatch.setattr(client.uploads, "upload_file", fake_upload_file)

    with pytest.raises(WeComRequestError, match="fileid"):
        client.smartsheet.upload_file_and_add_attachment_record(
            docid="DOCID",
            sheet_id="sheet-1",
            field_key="FILE_FIELD_ID",
            upload_request={
                "spaceid": "SPACEID",
                "fatherid": "FOLDERID",
                "file_name": "example.txt",
                "file_base64_content": "BASE64DATA",
            },
        )


def test_upload_file_and_add_attachment_record_raises_when_share_url_missing(
    client: WeComClient,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """开启 share_link 时，缺少 share_url 应抛出请求异常。"""

    def fake_upload_file(request: dict[str, object]) -> UploadFileResponse:
        return UploadFileResponse(fileid="FILEID")

    def fake_share_file(request: dict[str, object]) -> ShareFileResponse:
        return ShareFileResponse(share_url=None)

    monkeypatch.setattr(client.uploads, "upload_file", fake_upload_file)
    monkeypatch.setattr(client.uploads, "share_file", fake_share_file)

    with pytest.raises(WeComRequestError, match="share_url"):
        client.smartsheet.upload_file_and_add_attachment_record(
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


def test_upload_file_and_add_attachment_record_includes_share_url(
    client: WeComClient,
    bind_request_json: Callable[[dict[str, object]], dict[str, object]],
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """开启 share_link 时应将分享链接写入附件字段。"""

    captured = bind_request_json({"errcode": 0, "errmsg": "ok", "records": []})

    def fake_upload_file(request: dict[str, object]) -> UploadFileResponse:
        return UploadFileResponse(fileid="FILEID")

    def fake_share_file(request: dict[str, object]) -> ShareFileResponse:
        return ShareFileResponse(share_url="https://example.com/share")

    monkeypatch.setattr(client.uploads, "upload_file", fake_upload_file)
    monkeypatch.setattr(client.uploads, "share_file", fake_share_file)

    response = client.smartsheet.upload_file_and_add_attachment_record(
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
    assert captured["json"] == {
        "docid": "DOCID",
        "sheet_id": "sheet-1",
        "key_type": "CELL_VALUE_KEY_TYPE_FIELD_ID",
        "records": [
            {
                "values": {
                    "FILE_FIELD_ID": [
                        {"file_id": "FILEID", "file_url": "https://example.com/share"}
                    ]
                }
            }
        ],
    }


@pytest.mark.parametrize("conflict_key", ["file_id", "file_url"])
def test_upload_file_and_add_attachment_record_rejects_reserved_metadata_keys(
    client: WeComClient,
    monkeypatch: pytest.MonkeyPatch,
    conflict_key: str,
) -> None:
    """附件元数据不允许覆盖 helper 内部保留字段。"""

    def fake_upload_file(request: dict[str, object]) -> UploadFileResponse:
        return UploadFileResponse(fileid="FILEID")

    monkeypatch.setattr(client.uploads, "upload_file", fake_upload_file)

    with pytest.raises(ValueError, match="保留字段"):
        client.smartsheet.upload_file_and_add_attachment_record(
            docid="DOCID",
            sheet_id="sheet-1",
            field_key="FILE_FIELD_ID",
            upload_request={
                "spaceid": "SPACEID",
                "fatherid": "FOLDERID",
                "file_name": "example.txt",
                "file_base64_content": "BASE64DATA",
            },
            attachment_metadata={conflict_key: "X"},
        )


def test_add_field_group_serializes_children(
    client: WeComClient,
    bind_request_json: Callable[[dict[str, object]], dict[str, object]],
) -> None:
    """新增编组应正确序列化子字段引用。"""

    captured = bind_request_json(
        {
            "errcode": 0,
            "errmsg": "ok",
            "field_group": {
                "field_group_id": "group-1",
                "name": "基础信息",
                "children": [{"field_id": "field-1"}],
            },
        },
    )

    response = client.smartsheet.add_field_group(
        AddFieldGroupRequest(
            docid="DOCID",
            sheet_id="sheet-1",
            name="基础信息",
            children=[FieldGroupChild(field_id="field-1")],
        )
    )

    assert response.field_group is not None
    assert response.field_group.field_group_id == "group-1"
    assert captured["path"] == "/cgi-bin/wedoc/smartsheet/add_field_group"
    assert captured["json"] == {
        "docid": "DOCID",
        "sheet_id": "sheet-1",
        "name": "基础信息",
        "children": [{"field_id": "field-1"}],
    }


def test_add_sheet_requires_docid() -> None:
    """新增子表缺少必填字段时应校验失败。"""

    with pytest.raises(ValidationError):
        AddSheetRequest.model_validate({})


def test_add_view_requires_view_type() -> None:
    """新增视图缺少视图类型时应校验失败。"""

    with pytest.raises(ValidationError):
        AddViewRequest.model_validate(
            {"docid": "DOCID", "sheet_id": "sheet-1", "view_title": "全部任务"}
        )


def test_add_fields_requires_non_empty_list() -> None:
    """新增字段接口应拒绝缺少 fields 的入参。"""

    with pytest.raises(ValidationError):
        AddFieldsRequest.model_validate({"docid": "DOCID", "sheet_id": "sheet-1"})


def test_add_field_requires_field_type() -> None:
    """字段定义缺少字段类型时应校验失败。"""

    with pytest.raises(ValidationError):
        AddField.model_validate({"field_title": "任务名"})


@pytest.mark.parametrize(
    ("api_call", "request_payload", "response_payload", "expected_path"),
    [
        (
            "delete_sheet",
            {"docid": "DOCID", "sheet_id": "sheet-1"},
            {"errcode": 0, "errmsg": "ok"},
            "/cgi-bin/wedoc/smartsheet/delete_sheet",
        ),
        (
            "update_sheet",
            {
                "docid": "DOCID",
                "properties": {"sheet_id": "sheet-1", "title": "新标题"},
            },
            {"errcode": 0, "errmsg": "ok"},
            "/cgi-bin/wedoc/smartsheet/update_sheet",
        ),
        (
            "delete_views",
            {"docid": "DOCID", "sheet_id": "sheet-1", "view_ids": ["view-1"]},
            {"errcode": 0, "errmsg": "ok"},
            "/cgi-bin/wedoc/smartsheet/delete_views",
        ),
        (
            "update_view",
            {
                "docid": "DOCID",
                "sheet_id": "sheet-1",
                "view_id": "view-1",
                "view_title": "迭代视图",
            },
            {
                "errcode": 0,
                "errmsg": "ok",
                "view": {
                    "view_id": "view-1",
                    "view_title": "迭代视图",
                    "view_type": ViewType.VIEW_TYPE_GRID.value,
                },
            },
            "/cgi-bin/wedoc/smartsheet/update_view",
        ),
        (
            "delete_fields",
            {"docid": "DOCID", "sheet_id": "sheet-1", "field_ids": ["field-1"]},
            {"errcode": 0, "errmsg": "ok"},
            "/cgi-bin/wedoc/smartsheet/delete_fields",
        ),
        (
            "update_fields",
            {
                "docid": "DOCID",
                "sheet_id": "sheet-1",
                "fields": [
                    {
                        "field_id": "field-1",
                        "field_type": FieldType.FIELD_TYPE_TEXT.value,
                        "field_title": "任务名称",
                    }
                ],
            },
            {"errcode": 0, "errmsg": "ok", "fields": [{"field_id": "field-1"}]},
            "/cgi-bin/wedoc/smartsheet/update_fields",
        ),
        (
            "add_records",
            {
                "docid": "DOCID",
                "sheet_id": "sheet-1",
                "records": [{"values": {"任务名": "task-1"}}],
            },
            {
                "errcode": 0,
                "errmsg": "ok",
                "records": [{"record_id": "r1", "values": {"任务名": "task-1"}}],
            },
            "/cgi-bin/wedoc/smartsheet/add_records",
        ),
        (
            "delete_records",
            {"docid": "DOCID", "sheet_id": "sheet-1", "record_ids": ["r1"]},
            {"errcode": 0, "errmsg": "ok"},
            "/cgi-bin/wedoc/smartsheet/delete_records",
        ),
        (
            "update_records",
            {
                "docid": "DOCID",
                "sheet_id": "sheet-1",
                "records": [{"record_id": "r1", "values": {"任务名": "task-2"}}],
            },
            {
                "errcode": 0,
                "errmsg": "ok",
                "records": [{"record_id": "r1", "values": {"任务名": "task-2"}}],
            },
            "/cgi-bin/wedoc/smartsheet/update_records",
        ),
        (
            "update_field_group",
            {
                "docid": "DOCID",
                "sheet_id": "sheet-1",
                "field_group_id": "g1",
                "name": "新分组",
            },
            {"errcode": 0, "errmsg": "ok", "field_group": {"field_group_id": "g1"}},
            "/cgi-bin/wedoc/smartsheet/update_field_group",
        ),
        (
            "delete_field_groups",
            {"docid": "DOCID", "sheet_id": "sheet-1", "field_group_ids": ["g1"]},
            {"errcode": 0, "errmsg": "ok"},
            "/cgi-bin/wedoc/smartsheet/delete_field_groups",
        ),
    ],
)
def test_smartsheet_mutation_apis_use_expected_contract(
    client: WeComClient,
    bind_request_json: Callable[[dict[str, object]], dict[str, object]],
    api_call: str,
    request_payload: dict[str, object],
    response_payload: dict[str, object],
    expected_path: str,
) -> None:
    """各写接口应使用固定 endpoint，并正确透传请求体。"""

    captured = bind_request_json(response_payload)
    response = getattr(client.smartsheet, api_call)(request_payload)

    assert response.ok is True
    assert captured["method"] == "POST"
    assert captured["path"] == expected_path
    assert captured["json"] == request_payload


@pytest.mark.parametrize(
    ("api_call", "request_payload", "response_payload", "expected_path"),
    [
        (
            "get_sheet",
            {"docid": "DOCID"},
            {
                "errcode": 0,
                "errmsg": "ok",
                "sheet_list": [
                    {
                        "sheet_id": "sheet-1",
                        "title": "任务池",
                        "is_visible": True,
                        "type": "smartsheet",
                    }
                ],
            },
            "/cgi-bin/wedoc/smartsheet/get_sheet",
        ),
        (
            "get_views",
            {"docid": "DOCID", "sheet_id": "sheet-1"},
            {
                "errcode": 0,
                "errmsg": "ok",
                "total": 1,
                "views": [
                    {
                        "view_id": "view-1",
                        "view_title": "全部任务",
                        "view_type": ViewType.VIEW_TYPE_GRID.value,
                    }
                ],
            },
            "/cgi-bin/wedoc/smartsheet/get_views",
        ),
        (
            "get_fields",
            {"docid": "DOCID", "sheet_id": "sheet-1"},
            {
                "errcode": 0,
                "errmsg": "ok",
                "total": 1,
                "fields": [{"field_id": "field-1", "field_title": "任务名"}],
            },
            "/cgi-bin/wedoc/smartsheet/get_fields",
        ),
        (
            "get_field_groups",
            {"docid": "DOCID", "sheet_id": "sheet-1"},
            {
                "errcode": 0,
                "errmsg": "ok",
                "total": 1,
                "field_groups": [{"field_group_id": "g1", "name": "基础信息"}],
            },
            "/cgi-bin/wedoc/smartsheet/get_field_groups",
        ),
    ],
)
def test_smartsheet_query_apis_parse_response_and_path(
    client: WeComClient,
    bind_request_json: Callable[[dict[str, object]], dict[str, object]],
    api_call: str,
    request_payload: dict[str, object],
    response_payload: dict[str, object],
    expected_path: str,
) -> None:
    """各查询接口应解析响应并命中正确 endpoint。"""

    captured = bind_request_json(response_payload)
    response = getattr(client.smartsheet, api_call)(request_payload)

    assert response.ok is True
    assert captured["path"] == expected_path
    assert captured["json"] == request_payload


@pytest.mark.parametrize(
    "api_call,payload",
    [
        ("delete_sheet", {"docid": "DOCID"}),
        ("update_sheet", {"docid": "DOCID"}),
        ("delete_views", {"docid": "DOCID", "sheet_id": "sheet-1"}),
        ("update_view", {"docid": "DOCID", "sheet_id": "sheet-1"}),
        ("get_views", {"docid": "DOCID"}),
        ("delete_fields", {"docid": "DOCID", "sheet_id": "sheet-1"}),
        ("update_fields", {"docid": "DOCID", "sheet_id": "sheet-1"}),
        ("get_fields", {"docid": "DOCID"}),
        ("add_records", {"docid": "DOCID", "sheet_id": "sheet-1"}),
        ("delete_records", {"docid": "DOCID", "sheet_id": "sheet-1"}),
        ("update_records", {"docid": "DOCID", "sheet_id": "sheet-1"}),
        ("update_field_group", {"docid": "DOCID", "sheet_id": "sheet-1"}),
        ("delete_field_groups", {"docid": "DOCID", "sheet_id": "sheet-1"}),
        ("get_field_groups", {"docid": "DOCID"}),
    ],
)
def test_smartsheet_apis_raise_validation_error_for_invalid_payload(
    client: WeComClient,
    api_call: str,
    payload: dict[str, object],
) -> None:
    """关键接口在缺少必填参数时应抛出 ValidationError。"""

    with pytest.raises(ValidationError):
        getattr(client.smartsheet, api_call)(payload)
