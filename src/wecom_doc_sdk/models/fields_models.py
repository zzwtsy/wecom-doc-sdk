from __future__ import annotations

from typing import List, Optional

from pydantic import Field as PydanticField
from pydantic import model_validator

from .common import WeComBaseModel, WeComBaseResponse
from .fields_properties import (
    AttachmentFieldProperty,
    AutoNumberFieldProperty,
    BarcodeFieldProperty,
    CheckboxFieldProperty,
    CreatedTimeFieldProperty,
    CreatedUserFieldProperty,
    CurrencyFieldProperty,
    DateTimeFieldProperty,
    FieldType,
    LocationFieldProperty,
    ModifiedTimeFieldProperty,
    ModifiedUserFieldProperty,
    NumberFieldProperty,
    PercentageFieldProperty,
    ProgressFieldProperty,
    ReferenceFieldProperty,
    SelectFieldProperty,
    SingleSelectFieldProperty,
    TextFieldProperty,
    UrlFieldProperty,
    UserFieldProperty,
    WwGroupFieldProperty,
    _get_configured_field_properties,
    _validate_field_type_property_match,
)


class FieldModel(WeComBaseModel):
    """字段详情（查询/返回）。"""

    field_id: Optional[str] = PydanticField(default=None, description="字段 ID")
    field_title: Optional[str] = PydanticField(default=None, description="字段标题")
    field_type: Optional[FieldType] = PydanticField(
        default=None, description="字段类型"
    )
    property_text: Optional[TextFieldProperty] = PydanticField(
        default=None, description="文本字段属性"
    )
    property_number: Optional[NumberFieldProperty] = None
    property_checkbox: Optional[CheckboxFieldProperty] = None
    property_date_time: Optional[DateTimeFieldProperty] = None
    property_attachment: Optional[AttachmentFieldProperty] = None
    property_user: Optional[UserFieldProperty] = None
    property_url: Optional[UrlFieldProperty] = None
    property_select: Optional[SelectFieldProperty] = None
    property_created_user: Optional[CreatedUserFieldProperty] = PydanticField(
        default=None, description="创建人字段属性"
    )
    property_modified_user: Optional[ModifiedUserFieldProperty] = PydanticField(
        default=None, description="最后编辑人字段属性"
    )
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
    """新增字段定义。"""

    field_title: str = PydanticField(description="字段标题")
    field_type: FieldType = PydanticField(description="字段类型")
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

    @model_validator(mode="after")
    def validate_field_type_property_match(self) -> "AddField":
        return _validate_field_type_property_match(self)


class UpdateField(WeComBaseModel):
    """更新字段定义。"""

    field_id: str = PydanticField(description="字段 ID")
    field_title: Optional[str] = PydanticField(default=None, description="字段标题")
    field_type: FieldType = PydanticField(description="字段类型")
    property_text: Optional[TextFieldProperty] = PydanticField(
        default=None, description="文本字段属性"
    )
    property_number: Optional[NumberFieldProperty] = None
    property_checkbox: Optional[CheckboxFieldProperty] = None
    property_date_time: Optional[DateTimeFieldProperty] = None
    property_attachment: Optional[AttachmentFieldProperty] = None
    property_user: Optional[UserFieldProperty] = None
    property_url: Optional[UrlFieldProperty] = None
    property_select: Optional[SelectFieldProperty] = None
    property_created_user: Optional[CreatedUserFieldProperty] = PydanticField(
        default=None, description="创建人字段属性"
    )
    property_modified_user: Optional[ModifiedUserFieldProperty] = PydanticField(
        default=None, description="最后编辑人字段属性"
    )
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

    @model_validator(mode="after")
    def validate_update_payload(self) -> "UpdateField":
        _validate_field_type_property_match(self)

        configured_properties = _get_configured_field_properties(self)
        if self.field_title is None and not configured_properties:
            raise ValueError(
                "更新字段时至少填写 field_title 或与 field_type 匹配的字段属性"
            )
        return self


class AddFieldsRequest(WeComBaseModel):
    """添加字段请求体。"""

    docid: str = PydanticField(description="文档 ID")
    sheet_id: str = PydanticField(description="子表 ID")
    fields: List[AddField] = PydanticField(description="新增字段定义列表")


class AddFieldsResponse(WeComBaseResponse):
    """添加字段响应体。"""

    fields: Optional[List[FieldModel]] = PydanticField(
        default=None, description="新增后的字段列表"
    )


class UpdateFieldsRequest(WeComBaseModel):
    """更新字段请求体。"""

    docid: str = PydanticField(description="文档 ID")
    sheet_id: str = PydanticField(description="子表 ID")
    fields: List[UpdateField] = PydanticField(description="更新字段定义列表")


class UpdateFieldsResponse(WeComBaseResponse):
    """更新字段响应体。"""

    fields: Optional[List[FieldModel]] = PydanticField(
        default=None, description="更新后的字段列表"
    )


class DeleteFieldsRequest(WeComBaseModel):
    """删除字段请求体。"""

    docid: str = PydanticField(description="文档 ID")
    sheet_id: str = PydanticField(description="子表 ID")
    field_ids: List[str] = PydanticField(description="待删除字段 ID 列表")


class DeleteFieldsResponse(WeComBaseResponse):
    """删除字段响应体。"""

    pass


class GetFieldsRequest(WeComBaseModel):
    """查询字段请求体。"""

    docid: str = PydanticField(description="文档 ID")
    sheet_id: str = PydanticField(description="子表 ID")
    view_id: Optional[str] = PydanticField(default=None, description="视图 ID，可选")
    field_ids: Optional[List[str]] = PydanticField(
        default=None, description="字段 ID 列表，可选"
    )
    field_titles: Optional[List[str]] = PydanticField(
        default=None, description="字段标题列表，可选"
    )
    offset: Optional[int] = PydanticField(default=None, description="分页偏移量")
    limit: Optional[int] = PydanticField(default=None, description="分页大小")


class GetFieldsResponse(WeComBaseResponse):
    """查询字段响应体。"""

    total: Optional[int] = PydanticField(default=None, description="总数量")
    fields: Optional[List[FieldModel]] = PydanticField(
        default=None, description="字段列表"
    )


Field: type[FieldModel] = FieldModel


__all__ = [
    "AddField",
    "AddFieldsRequest",
    "AddFieldsResponse",
    "DeleteFieldsRequest",
    "DeleteFieldsResponse",
    "Field",
    "FieldModel",
    "GetFieldsRequest",
    "GetFieldsResponse",
    "UpdateField",
    "UpdateFieldsRequest",
    "UpdateFieldsResponse",
]
