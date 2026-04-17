from __future__ import annotations

import pytest
from pydantic import ValidationError

from wecom_doc_sdk.models.enums import FieldType
from wecom_doc_sdk.models.fields import (
    FIELD_TYPE_PROPERTY_NAME_MAP,
    AddFieldsRequest,
    Field,
    FieldModel,
    Option,
    UpdateField,
)


def test_fields_module_exports_compatible_symbols() -> None:
    """兼容导出层应继续暴露常用字段模型和别名。"""

    request = AddFieldsRequest.model_validate(
        {
            "docid": "DOCID",
            "sheet_id": "sheet-1",
            "fields": [
                {
                    "field_title": "任务名",
                    "field_type": FieldType.FIELD_TYPE_TEXT,
                }
            ],
        }
    )
    option = Option.model_validate({"text": "进行中"})

    assert request.fields[0].field_title == "任务名"
    assert option.text == "进行中"
    assert Field is FieldModel
    assert FIELD_TYPE_PROPERTY_NAME_MAP[FieldType.FIELD_TYPE_TEXT] == "property_text"


def test_fields_module_update_field_validation_still_works() -> None:
    """兼容导出层应保留 UpdateField 的跨字段校验。"""

    with pytest.raises(ValidationError, match="仅支持 property_text"):
        UpdateField.model_validate(
            {
                "field_id": "field-1",
                "field_type": FieldType.FIELD_TYPE_TEXT,
                "property_number": {"decimal_places": 2},
            }
        )
