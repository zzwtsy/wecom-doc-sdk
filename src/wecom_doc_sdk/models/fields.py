from __future__ import annotations

from typing import List, Optional

from pydantic import AliasChoices, Field
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
    """单选/多选字段中的选项定义。"""

    # 已存在选项优先通过 ID 识别；新增选项时可为空。
    id: Optional[str] = Field(default=None, description="选项 ID")
    # 新增选项时可指定官方色板编号。
    style: Optional[Style] = Field(default=None, description="选项颜色样式")
    # 选项展示文本。
    text: Optional[str] = Field(default=None, description="选项文本")


class NumberRule(WeComBaseModel):
    """自动编号规则项。"""

    type: Optional[NumberRuleType] = None
    # 值的语义取决于规则类型，可能是时间格式、固定字符或自增位数。
    value: Optional[str] = None


class NumberFieldProperty(WeComBaseModel):
    """数字字段属性。"""

    decimal_places: Optional[DecimalPlaces] = None
    # 是否启用千位分隔符显示。
    use_separate: Optional[bool] = None


class CheckboxFieldProperty(WeComBaseModel):
    """复选框字段属性。"""

    # 新建记录时是否默认勾选。
    checked: Optional[bool] = None


class DateTimeFieldProperty(WeComBaseModel):
    """日期字段属性。"""

    format: Optional[str] = None
    # 新建记录时是否自动填充当前时间。
    auto_fill: Optional[bool] = None


class AttachmentFieldProperty(WeComBaseModel):
    """文件字段属性。"""

    display_mode: Optional[DisplayMode] = None


class UserFieldProperty(WeComBaseModel):
    """人员字段属性。"""

    # 是否允许一次选择多个成员。
    is_multiple: Optional[bool] = None
    # 添加成员时是否通知用户。
    is_notified: Optional[bool] = None


class UrlFieldProperty(WeComBaseModel):
    """超链接字段属性。"""

    type: Optional[LinkType] = None


class SelectFieldProperty(WeComBaseModel):
    """多选字段属性。"""

    # 是否允许在填写时直接创建新选项。
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

    # 关联的子表 ID；为空时表示关联当前子表。
    sub_id: Optional[str] = None
    # 官方文档长期使用了拼写错误 `filed_id`，这里兼容 `filed_id/field_id` 两种输入。
    field_id: Optional[str] = PydanticField(
        default=None,
        validation_alias=AliasChoices("filed_id", "field_id"),
        serialization_alias="filed_id",
    )
    # 是否允许多选关联记录。
    is_multiple: Optional[bool] = None
    view_id: Optional[str] = None


class LocationFieldProperty(WeComBaseModel):
    """地理位置字段属性。"""

    input_type: Optional[LocationInputType] = None


class AutoNumberFieldProperty(WeComBaseModel):
    """自动编号字段属性。"""

    type: Optional[NumberType] = None
    rules: Optional[List[NumberRule]] = None
    # 是否将新的编号规则应用到已有记录。
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

    # 为 `True` 时仅允许手机扫码录入。
    mobile_scan_only: Optional[bool] = None


class TextFieldProperty(WeComBaseModel):
    """文本字段属性。"""


class CreatedUserFieldProperty(WeComBaseModel):
    """创建人字段属性。"""


class ModifiedUserFieldProperty(WeComBaseModel):
    """最后编辑人字段属性。"""


class FieldModel(WeComBaseModel):
    """字段详情（查询/返回）。

    企业微信字段类型与字段属性是一一对应关系，只有匹配 `field_type` 的
    `property_*` 字段才会有意义。
    """

    field_id: Optional[str] = Field(default=None, description="字段 ID")
    field_title: Optional[str] = Field(default=None, description="字段标题")
    field_type: Optional[FieldType] = Field(default=None, description="字段类型")
    # 文本、创建人、最后编辑人等字段使用无参属性对象承载。
    property_text: Optional[TextFieldProperty] = Field(
        default=None, description="文本字段属性"
    )
    # 以下 `property_*` 字段与 `field_type` 一一对应。
    property_number: Optional[NumberFieldProperty] = None
    property_checkbox: Optional[CheckboxFieldProperty] = None
    property_date_time: Optional[DateTimeFieldProperty] = None
    property_attachment: Optional[AttachmentFieldProperty] = None
    property_user: Optional[UserFieldProperty] = None
    property_url: Optional[UrlFieldProperty] = None
    property_select: Optional[SelectFieldProperty] = None
    property_created_user: Optional[CreatedUserFieldProperty] = Field(
        default=None, description="创建人字段属性"
    )
    property_modified_user: Optional[ModifiedUserFieldProperty] = Field(
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

    field_title: str = Field(description="字段标题")
    field_type: FieldType = Field(description="字段类型")
    # 新增字段时只填写与 `field_type` 匹配的属性结构。
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
    """更新字段定义。

    企业微信只允许更新字段标题和字段属性，不允许通过该接口修改字段类型。
    """

    # 需要更新的字段 ID。
    field_id: str = Field(description="字段 ID")
    field_title: Optional[str] = Field(default=None, description="字段标题")
    # 必须与原字段类型一致，用于让接口识别当前字段属性结构。
    field_type: FieldType = Field(description="字段类型")
    property_text: Optional[TextFieldProperty] = Field(
        default=None, description="文本字段属性"
    )
    property_number: Optional[NumberFieldProperty] = None
    property_checkbox: Optional[CheckboxFieldProperty] = None
    property_date_time: Optional[DateTimeFieldProperty] = None
    property_attachment: Optional[AttachmentFieldProperty] = None
    property_user: Optional[UserFieldProperty] = None
    property_url: Optional[UrlFieldProperty] = None
    property_select: Optional[SelectFieldProperty] = None
    property_created_user: Optional[CreatedUserFieldProperty] = Field(
        default=None, description="创建人字段属性"
    )
    property_modified_user: Optional[ModifiedUserFieldProperty] = Field(
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


class AddFieldsRequest(WeComBaseModel):
    """添加字段请求体。"""

    docid: str = Field(description="文档 ID")
    sheet_id: str = Field(description="子表 ID")
    # 单次可提交一个或多个字段定义；单表字段总数上限为 150。
    fields: List[AddField] = Field(description="新增字段定义列表")


class AddFieldsResponse(WeComBaseResponse):
    """添加字段响应体。"""

    fields: Optional[List[FieldModel]] = Field(
        default=None, description="新增后的字段列表"
    )


class UpdateFieldsRequest(WeComBaseModel):
    """更新字段请求体。"""

    docid: str = Field(description="文档 ID")
    sheet_id: str = Field(description="子表 ID")
    fields: List[UpdateField] = Field(description="更新字段定义列表")


class UpdateFieldsResponse(WeComBaseResponse):
    """更新字段响应体。"""

    fields: Optional[List[FieldModel]] = Field(
        default=None, description="更新后的字段列表"
    )


class DeleteFieldsRequest(WeComBaseModel):
    """删除字段请求体。"""

    docid: str = Field(description="文档 ID")
    sheet_id: str = Field(description="子表 ID")
    field_ids: List[str] = Field(description="待删除字段 ID 列表")


class DeleteFieldsResponse(WeComBaseResponse):
    """删除字段响应体。"""

    pass


class GetFieldsRequest(WeComBaseModel):
    """查询字段请求体。"""

    docid: str = Field(description="文档 ID")
    sheet_id: str = Field(description="子表 ID")
    # 指定视图后，仅返回该视图下相关字段信息。
    view_id: Optional[str] = Field(default=None, description="视图 ID，可选")
    field_ids: Optional[List[str]] = Field(
        default=None, description="字段 ID 列表，可选"
    )
    field_titles: Optional[List[str]] = Field(
        default=None, description="字段标题列表，可选"
    )
    offset: Optional[int] = Field(default=None, description="分页偏移量")
    # 单次 `limit` 最大为 1000；不传或为 0 时由接口按默认规则返回。
    limit: Optional[int] = Field(default=None, description="分页大小")


class GetFieldsResponse(WeComBaseResponse):
    """查询字段响应体。"""

    total: Optional[int] = Field(default=None, description="总数量")
    fields: Optional[List[FieldModel]] = Field(default=None, description="字段列表")


# 兼容文档命名：对外可使用 Field
Field: type[FieldModel] = FieldModel
