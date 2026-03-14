from __future__ import annotations

from typing import Any, List, Optional

from pydantic import AliasChoices
from pydantic import Field as PydanticField

from .common import WeComBaseModel, WeComBaseResponse
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


class Option(WeComBaseModel):
    """选项（用于单选/多选）。"""

    id: Optional[str] = None
    style: Optional[Style] = None
    text: Optional[str] = None


class NumberRule(WeComBaseModel):
    """自动编号规则。"""

    type: Optional[NumberRuleType] = None
    value: Optional[str] = None


class NumberFieldProperty(WeComBaseModel):
    decimal_places: Optional[DecimalPlaces] = None
    use_separate: Optional[bool] = None


class CheckboxFieldProperty(WeComBaseModel):
    checked: Optional[bool] = None


class DateTimeFieldProperty(WeComBaseModel):
    format: Optional[str] = None
    auto_fill: Optional[bool] = None


class AttachmentFieldProperty(WeComBaseModel):
    display_mode: Optional[DisplayMode] = None


class UserFieldProperty(WeComBaseModel):
    is_multiple: Optional[bool] = None
    is_notified: Optional[bool] = None


class UrlFieldProperty(WeComBaseModel):
    type: Optional[LinkType] = None


class SelectFieldProperty(WeComBaseModel):
    is_quick_add: Optional[bool] = None
    options: Optional[List[Option]] = None


class CreatedTimeFieldProperty(WeComBaseModel):
    format: Optional[str] = None


class ModifiedTimeFieldProperty(WeComBaseModel):
    format: Optional[str] = None


class ProgressFieldProperty(WeComBaseModel):
    decimal_places: Optional[DecimalPlaces] = None


class SingleSelectFieldProperty(WeComBaseModel):
    is_quick_add: Optional[bool] = None
    options: Optional[List[Option]] = None


class ReferenceFieldProperty(WeComBaseModel):
    sub_id: Optional[str] = None
    field_id: Optional[str] = PydanticField(
        default=None,
        validation_alias=AliasChoices("filed_id", "field_id"),
        serialization_alias="filed_id",
    )
    is_multiple: Optional[bool] = None
    view_id: Optional[str] = None


class LocationFieldProperty(WeComBaseModel):
    input_type: Optional[LocationInputType] = None


class AutoNumberFieldProperty(WeComBaseModel):
    type: Optional[NumberType] = None
    rules: Optional[List[NumberRule]] = None
    reformat_existing_record: Optional[bool] = None


class CurrencyFieldProperty(WeComBaseModel):
    currency_type: Optional[CurrencyType] = None
    decimal_places: Optional[DecimalPlaces] = None
    use_separate: Optional[bool] = None


class WwGroupFieldProperty(WeComBaseModel):
    allow_multiple: Optional[bool] = None


class PercentageFieldProperty(WeComBaseModel):
    decimal_places: Optional[DecimalPlaces] = None
    use_separate: Optional[bool] = None


class BarcodeFieldProperty(WeComBaseModel):
    mobile_scan_only: Optional[bool] = None


class FieldModel(WeComBaseModel):
    """字段详情（查询/返回）。"""

    field_id: Optional[str] = None
    field_title: Optional[str] = None
    field_type: Optional[FieldType] = None
    property_text: Optional[dict[str, Any]] = None
    property_number: Optional[NumberFieldProperty] = None
    property_checkbox: Optional[CheckboxFieldProperty] = None
    property_date_time: Optional[DateTimeFieldProperty] = None
    property_attachment: Optional[AttachmentFieldProperty] = None
    property_user: Optional[UserFieldProperty] = None
    property_url: Optional[UrlFieldProperty] = None
    property_select: Optional[SelectFieldProperty] = None
    property_created_user: Optional[dict[str, Any]] = None
    property_modified_user: Optional[dict[str, Any]] = None
    property_created_time: Optional[CreatedTimeFieldProperty] = None
    property_modified_time: Optional[ModifiedTimeFieldProperty] = None
    property_progress: Optional[ProgressFieldProperty] = None
    property_single_select: Optional[SingleSelectFieldProperty] = None
    property_reference: Optional[ReferenceFieldProperty] = None
    property_location: Optional[LocationFieldProperty] = None
    property_auto_number: Optional[AutoNumberFieldProperty] = None
    property_currency: Optional[CurrencyFieldProperty] = None
    property_ww_group: Optional[WwGroupFieldProperty] = None
    property_percentage: Optional[PercentageFieldProperty] = None
    property_barcode: Optional[BarcodeFieldProperty] = None


class AddField(WeComBaseModel):
    """新增字段。"""

    field_title: str
    field_type: FieldType
    property_number: Optional[NumberFieldProperty] = None
    property_checkbox: Optional[CheckboxFieldProperty] = None
    property_date_time: Optional[DateTimeFieldProperty] = None
    property_attachment: Optional[AttachmentFieldProperty] = None
    property_user: Optional[UserFieldProperty] = None
    property_url: Optional[UrlFieldProperty] = None
    property_select: Optional[SelectFieldProperty] = None
    property_created_time: Optional[CreatedTimeFieldProperty] = None
    property_modified_time: Optional[ModifiedTimeFieldProperty] = None
    property_progress: Optional[ProgressFieldProperty] = None
    property_single_select: Optional[SingleSelectFieldProperty] = None
    property_reference: Optional[ReferenceFieldProperty] = None
    property_location: Optional[LocationFieldProperty] = None
    property_auto_number: Optional[AutoNumberFieldProperty] = None
    property_currency: Optional[CurrencyFieldProperty] = None
    property_ww_group: Optional[WwGroupFieldProperty] = None
    property_percentage: Optional[PercentageFieldProperty] = None
    property_barcode: Optional[BarcodeFieldProperty] = None


class UpdateField(WeComBaseModel):
    """更新字段。"""

    field_id: str
    field_title: Optional[str] = None
    field_type: FieldType
    property_text: Optional[dict[str, Any]] = None
    property_number: Optional[NumberFieldProperty] = None
    property_checkbox: Optional[CheckboxFieldProperty] = None
    property_date_time: Optional[DateTimeFieldProperty] = None
    property_attachment: Optional[AttachmentFieldProperty] = None
    property_user: Optional[UserFieldProperty] = None
    property_url: Optional[UrlFieldProperty] = None
    property_select: Optional[SelectFieldProperty] = None
    property_created_user: Optional[dict[str, Any]] = None
    property_modified_user: Optional[dict[str, Any]] = None
    property_created_time: Optional[CreatedTimeFieldProperty] = None
    property_modified_time: Optional[ModifiedTimeFieldProperty] = None
    property_progress: Optional[ProgressFieldProperty] = None
    property_single_select: Optional[SingleSelectFieldProperty] = None
    property_reference: Optional[ReferenceFieldProperty] = None
    property_location: Optional[LocationFieldProperty] = None
    property_auto_number: Optional[AutoNumberFieldProperty] = None
    property_currency: Optional[CurrencyFieldProperty] = None
    property_ww_group: Optional[WwGroupFieldProperty] = None
    property_percentage: Optional[PercentageFieldProperty] = None
    property_barcode: Optional[BarcodeFieldProperty] = None


class AddFieldsRequest(WeComBaseModel):
    docid: str
    sheet_id: str
    fields: List[AddField]


class AddFieldsResponse(WeComBaseResponse):
    fields: Optional[List[FieldModel]] = None


class UpdateFieldsRequest(WeComBaseModel):
    docid: str
    sheet_id: str
    fields: List[UpdateField]


class UpdateFieldsResponse(WeComBaseResponse):
    fields: Optional[List[FieldModel]] = None


class DeleteFieldsRequest(WeComBaseModel):
    docid: str
    sheet_id: str
    field_ids: List[str]


class DeleteFieldsResponse(WeComBaseResponse):
    pass


class GetFieldsRequest(WeComBaseModel):
    docid: str
    sheet_id: str
    view_id: Optional[str] = None
    field_ids: Optional[List[str]] = None
    field_titles: Optional[List[str]] = None
    offset: Optional[int] = None
    limit: Optional[int] = None


class GetFieldsResponse(WeComBaseResponse):
    total: Optional[int] = None
    fields: Optional[List[FieldModel]] = None

# 兼容文档命名：对外可使用 Field
Field = FieldModel

