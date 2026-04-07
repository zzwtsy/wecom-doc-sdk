from __future__ import annotations

from collections.abc import Callable

import pytest
from pydantic import ValidationError

from wecom_doc_sdk import WeComClient
from wecom_doc_sdk.models.fields import AddField, AddFieldsRequest, FieldType
from wecom_doc_sdk.models.groups import AddFieldGroupRequest
from wecom_doc_sdk.models.sheets import AddSheetRequest
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
        AddSheetRequest(docid="DOCID", properties={"title": "迭代计划", "index": 1})
    )

    assert response.properties is not None
    assert response.properties.sheet_id == "sheet-1"
    assert captured["path"] == "/cgi-bin/wedoc/smartsheet/add_sheet"
    assert captured["json"] == {"docid": "DOCID", "properties": {"title": "迭代计划", "index": 1}}


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
            children=[{"field_id": "field-1"}],
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
