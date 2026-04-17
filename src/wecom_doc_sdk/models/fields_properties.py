from __future__ import annotations

from typing import Any, List, Optional

from pydantic import AliasChoices, ConfigDict, Field
from pydantic import Field as PydanticField

from .common import WeComBaseModel
from .enums import (
    CurrencyType,
    DecimalPlaces,
    DisplayMode,
    FieldType,
    LinkType,
    LocationInputType,
    NumberRuleType,
    NumberType,
    Style,
)

FIELD_TYPE_PROPERTY_NAME_MAP: dict[FieldType, str | None] = {
    FieldType.FIELD_TYPE_TEXT: "property_text",
    FieldType.FIELD_TYPE_NUMBER: "property_number",
    FieldType.FIELD_TYPE_CHECKBOX: "property_checkbox",
    FieldType.FIELD_TYPE_DATE_TIME: "property_date_time",
    FieldType.FIELD_TYPE_IMAGE: None,
    FieldType.FIELD_TYPE_ATTACHMENT: "property_attachment",
    FieldType.FIELD_TYPE_USER: "property_user",
    FieldType.FIELD_TYPE_URL: "property_url",
    FieldType.FIELD_TYPE_SELECT: "property_select",
    FieldType.FIELD_TYPE_CREATED_USER: "property_created_user",
    FieldType.FIELD_TYPE_MODIFIED_USER: "property_modified_user",
    FieldType.FIELD_TYPE_CREATED_TIME: "property_created_time",
    FieldType.FIELD_TYPE_MODIFIED_TIME: "property_modified_time",
    FieldType.FIELD_TYPE_PROGRESS: "property_progress",
    FieldType.FIELD_TYPE_PHONE_NUMBER: None,
    FieldType.FIELD_TYPE_EMAIL: None,
    FieldType.FIELD_TYPE_SINGLE_SELECT: "property_single_select",
    FieldType.FIELD_TYPE_REFERENCE: "property_reference",
    FieldType.FIELD_TYPE_LOCATION: "property_location",
    FieldType.FIELD_TYPE_FORMULA: None,
    FieldType.FIELD_TYPE_CURRENCY: "property_currency",
    FieldType.FIELD_TYPE_WWGROUP: "property_ww_group",
    FieldType.FIELD_TYPE_AUTONUMBER: "property_auto_number",
    FieldType.FIELD_TYPE_PERCENTAGE: "property_percentage",
    FieldType.FIELD_TYPE_BARCODE: "property_barcode",
}

FIELD_PROPERTY_NAMES: tuple[str, ...] = (
    "property_text",
    "property_number",
    "property_checkbox",
    "property_date_time",
    "property_attachment",
    "property_user",
    "property_url",
    "property_select",
    "property_created_user",
    "property_modified_user",
    "property_created_time",
    "property_modified_time",
    "property_progress",
    "property_single_select",
    "property_reference",
    "property_location",
    "property_auto_number",
    "property_currency",
    "property_ww_group",
    "property_percentage",
    "property_barcode",
)


def _get_configured_field_properties(model: Any) -> list[str]:
    """返回当前字段模型中被显式设置的属性字段名。"""

    return [
        property_name
        for property_name in FIELD_PROPERTY_NAMES
        if getattr(model, property_name, None) is not None
    ]


def _validate_field_type_property_match(model: Any) -> Any:
    """校验字段类型与字段属性的一一对应关系。"""

    configured_properties = _get_configured_field_properties(model)
    expected_property = FIELD_TYPE_PROPERTY_NAME_MAP[model.field_type]

    if expected_property is None:
        if configured_properties:
            raise ValueError(
                f"{model.field_type.value} 不支持字段属性："
                f"{', '.join(configured_properties)}"
            )
        return model

    invalid_properties = [
        property_name
        for property_name in configured_properties
        if property_name != expected_property
    ]
    if invalid_properties:
        raise ValueError(
            f"{model.field_type.value} 仅支持 {expected_property}，"
            f"不能同时填写：{', '.join(invalid_properties)}"
        )
    return model


class Option(WeComBaseModel):
    """单选/多选字段中的选项定义。"""

    model_config = ConfigDict(extra="forbid")

    id: Optional[str] = Field(default=None, description="选项 ID")
    style: Optional[Style] = Field(default=None, description="选项颜色样式")
    text: Optional[str] = Field(default=None, description="选项文本")


class NumberRule(WeComBaseModel):
    """自动编号规则项。"""

    type: Optional[NumberRuleType] = None
    value: Optional[str] = None


class NumberFieldProperty(WeComBaseModel):
    """数字字段属性。"""

    decimal_places: Optional[DecimalPlaces] = None
    use_separate: Optional[bool] = None


class CheckboxFieldProperty(WeComBaseModel):
    """复选框字段属性。"""

    checked: Optional[bool] = None


class DateTimeFieldProperty(WeComBaseModel):
    """日期字段属性。"""

    format: Optional[str] = None
    auto_fill: Optional[bool] = None


class AttachmentFieldProperty(WeComBaseModel):
    """文件字段属性。"""

    display_mode: Optional[DisplayMode] = None


class UserFieldProperty(WeComBaseModel):
    """人员字段属性。"""

    is_multiple: Optional[bool] = None
    is_notified: Optional[bool] = None


class UrlFieldProperty(WeComBaseModel):
    """超链接字段属性。"""

    type: Optional[LinkType] = None


class SelectFieldProperty(WeComBaseModel):
    """多选字段属性。"""

    is_quick_add: Optional[bool] = None
    options: Optional[List[Option]] = None


class CreatedTimeFieldProperty(WeComBaseModel):
    """创建时间字段属性。"""

    format: Optional[str] = None


class ModifiedTimeFieldProperty(WeComBaseModel):
    """最后编辑时间字段属性。"""

    format: Optional[str] = None


class ProgressFieldProperty(WeComBaseModel):
    """进度字段属性。"""

    decimal_places: Optional[DecimalPlaces] = None


class SingleSelectFieldProperty(WeComBaseModel):
    """单选字段属性。"""

    is_quick_add: Optional[bool] = None
    options: Optional[List[Option]] = None


class ReferenceFieldProperty(WeComBaseModel):
    """关联字段属性。"""

    sub_id: Optional[str] = None
    field_id: Optional[str] = PydanticField(
        default=None,
        validation_alias=AliasChoices("filed_id", "field_id"),
        serialization_alias="filed_id",
    )
    is_multiple: Optional[bool] = None
    view_id: Optional[str] = None


class LocationFieldProperty(WeComBaseModel):
    """地理位置字段属性。"""

    input_type: Optional[LocationInputType] = None


class AutoNumberFieldProperty(WeComBaseModel):
    """自动编号字段属性。"""

    type: Optional[NumberType] = None
    rules: Optional[List[NumberRule]] = None
    reformat_existing_record: Optional[bool] = None


class CurrencyFieldProperty(WeComBaseModel):
    """货币字段属性。"""

    currency_type: Optional[CurrencyType] = None
    decimal_places: Optional[DecimalPlaces] = None
    use_separate: Optional[bool] = None


class WwGroupFieldProperty(WeComBaseModel):
    """群字段属性。"""

    allow_multiple: Optional[bool] = None


class PercentageFieldProperty(WeComBaseModel):
    """百分数字段属性。"""

    decimal_places: Optional[DecimalPlaces] = None
    use_separate: Optional[bool] = None


class BarcodeFieldProperty(WeComBaseModel):
    """条码字段属性。"""

    mobile_scan_only: Optional[bool] = None


class TextFieldProperty(WeComBaseModel):
    """文本字段属性。"""


class CreatedUserFieldProperty(WeComBaseModel):
    """创建人字段属性。"""


class ModifiedUserFieldProperty(WeComBaseModel):
    """最后编辑人字段属性。"""


__all__ = [
    "AttachmentFieldProperty",
    "AutoNumberFieldProperty",
    "BarcodeFieldProperty",
    "CheckboxFieldProperty",
    "CreatedTimeFieldProperty",
    "CreatedUserFieldProperty",
    "CurrencyFieldProperty",
    "CurrencyType",
    "DateTimeFieldProperty",
    "DecimalPlaces",
    "DisplayMode",
    "FIELD_PROPERTY_NAMES",
    "FIELD_TYPE_PROPERTY_NAME_MAP",
    "FieldType",
    "LinkType",
    "LocationFieldProperty",
    "LocationInputType",
    "ModifiedTimeFieldProperty",
    "ModifiedUserFieldProperty",
    "NumberFieldProperty",
    "NumberRule",
    "NumberRuleType",
    "NumberType",
    "Option",
    "PercentageFieldProperty",
    "ProgressFieldProperty",
    "ReferenceFieldProperty",
    "SelectFieldProperty",
    "SingleSelectFieldProperty",
    "Style",
    "TextFieldProperty",
    "UrlFieldProperty",
    "UserFieldProperty",
    "WwGroupFieldProperty",
    "_get_configured_field_properties",
    "_validate_field_type_property_match",
]
