from __future__ import annotations

from typing import Dict, List, Optional

from pydantic import AliasChoices, Field

from .common import WeComBaseModel, WeComBaseResponse
from .enums import (
    Conjunction,
    DateTimeType,
    FieldType,
    Operator,
    ViewColor,
    ViewColorConditionType,
    ViewType,
)


class StringValue(WeComBaseModel):
    """字符串型筛选值。

    适用于文本、超链接、电话、邮箱、地理位置、单选、多选等字段。
    """

    value: List[str] = Field(description="字符串筛选值列表")


class NumberValue(WeComBaseModel):
    """数字型筛选值。"""

    value: float = Field(description="数字筛选值")


class BoolValue(WeComBaseModel):
    """布尔型筛选值。"""

    value: bool = Field(description="布尔筛选值")


class UserValue(WeComBaseModel):
    """成员型筛选值。"""

    # 成员、创建人、最后编辑人等字段统一使用成员 ID 数组。
    value: List[str] = Field(description="成员 ID 列表")


class FilterDateTimeValue(WeComBaseModel):
    """日期型筛选值。"""

    # 日期筛选的模式，如今天、昨天或具体日期。
    type: DateTimeType = Field(description="日期筛选类型")
    # 当 `type` 为具体日期时使用毫秒级时间戳列表。
    value: List[str] = Field(description="日期筛选值列表")


class Condition(WeComBaseModel):
    """过滤条件。

    不同字段类型支持的操作符和值结构不同，调用方需要保证 `field_type`、
    `operator` 与对应的 `*_value` 组合合法。
    """

    field_id: str = Field(description="字段 ID")
    field_type: Optional[FieldType] = Field(default=None, description="字段类型")
    operator: Operator = Field(description="筛选操作符")
    string_value: Optional[StringValue] = None
    number_value: Optional[NumberValue] = None
    bool_value: Optional[BoolValue] = None
    user_value: Optional[UserValue] = None
    date_time_value: Optional[FilterDateTimeValue] = None


class SortInfo(WeComBaseModel):
    """单个字段的排序配置。"""

    field_id: str
    # `True` 表示降序；为空时按接口默认升序处理。
    desc: Optional[bool] = None


class SortSpec(WeComBaseModel):
    """视图排序配置。"""

    sort_infos: Optional[List[SortInfo]] = None


class GroupInfo(WeComBaseModel):
    """单个字段的分组配置。"""

    field_id: str
    desc: Optional[bool] = None


class GroupSpec(WeComBaseModel):
    """视图分组配置。"""

    groups: Optional[List[GroupInfo]] = None


class FilterSpec(WeComBaseModel):
    """视图或记录查询使用的过滤配置。"""

    # 多个条件之间按 AND 还是 OR 组合。
    conjunction: Conjunction = Field(description="条件连接符")
    conditions: List[Condition] = Field(description="筛选条件列表")


class ViewColorCondition(WeComBaseModel):
    """单条视图填色规则。"""

    # 更新填色规则时回传；新增时通常不需要传入。
    id: Optional[str] = None
    type: ViewColorConditionType
    color: ViewColor
    # 官方文档在不同位置曾使用 `condition`/`conditions` 两种命名，
    # 这里统一兼容输入，序列化时始终输出接口实际需要的 `condition`。
    condition: Optional[Condition] = Field(
        default=None,
        validation_alias=AliasChoices("condition", "conditions"),
        serialization_alias="condition",
    )


class ViewColorConfig(WeComBaseModel):
    """视图填色配置。"""

    conditions: List[ViewColorCondition]


class ViewProperty(WeComBaseModel):
    """视图属性配置。

    用于表达排序、分组、过滤、字段可见性、冻结列和条件填色等能力。
    """

    # 记录变化后是否自动重新套用排序规则。
    auto_sort: Optional[bool] = None
    sort_spec: Optional[SortSpec] = None
    group_spec: Optional[GroupSpec] = None
    filter_spec: Optional[FilterSpec] = None
    # 是否开启视图中的字段统计能力。
    is_field_stat_enabled: Optional[bool] = None
    # 类似 map：key 为字段 ID，value 为是否显示该字段。
    field_visibility: Optional[Dict[str, bool]] = None
    # 冻结列数量，从首列开始计算。
    frozen_field_count: Optional[int] = None
    color_config: Optional[ViewColorConfig] = None


class View(WeComBaseModel):
    """视图信息。"""

    view_id: str = Field(description="视图 ID")
    view_title: str = Field(description="视图标题")
    view_type: ViewType = Field(description="视图类型")
    property: Optional[ViewProperty] = Field(default=None, description="视图属性")


class GanttViewProperty(WeComBaseModel):
    """甘特视图专属属性。"""

    # 时间条起点字段，必须为日期类型字段 ID。
    start_date_field_id: str
    # 时间条终点字段，必须为日期类型字段 ID。
    end_date_field_id: str


class CalendarViewProperty(WeComBaseModel):
    """日历视图专属属性。"""

    start_date_field_id: str
    end_date_field_id: str


class AddViewRequest(WeComBaseModel):
    """添加视图请求体。"""

    docid: str = Field(description="文档 ID")
    sheet_id: str = Field(description="子表 ID")
    view_title: str = Field(description="视图标题")
    view_type: ViewType = Field(description="视图类型")
    # 仅在添加甘特视图时使用。
    property_gantt: Optional[GanttViewProperty] = None
    # 仅在添加日历视图时使用。
    property_calendar: Optional[CalendarViewProperty] = None


class AddViewResponse(WeComBaseResponse):
    """添加视图响应体。"""

    view: Optional[View] = Field(default=None, description="新增视图信息")


class DeleteViewsRequest(WeComBaseModel):
    """删除视图请求体。"""

    docid: str = Field(description="文档 ID")
    sheet_id: str = Field(description="子表 ID")
    view_ids: List[str] = Field(description="待删除视图 ID 列表")


class DeleteViewsResponse(WeComBaseResponse):
    """删除视图响应体。"""

    pass


class UpdateViewRequest(WeComBaseModel):
    """更新视图请求体。"""

    docid: str = Field(description="文档 ID")
    sheet_id: str = Field(description="子表 ID")
    view_id: str = Field(description="视图 ID")
    view_title: Optional[str] = Field(default=None, description="更新后的视图标题")
    # 支持更新排序、过滤、分组、字段显示、冻结列和填色等属性。
    property: Optional[ViewProperty] = Field(
        default=None, description="更新后的视图属性"
    )


class UpdateViewResponse(WeComBaseResponse):
    """更新视图响应体。"""

    view: Optional[View] = Field(default=None, description="更新后的视图信息")


class GetViewsRequest(WeComBaseModel):
    """查询视图请求体。"""

    docid: str = Field(description="文档 ID")
    sheet_id: str = Field(description="子表 ID")
    # 为空时查询子表中的全部视图。
    view_ids: Optional[List[str]] = Field(
        default=None, description="指定查询的视图 ID 列表"
    )
    offset: Optional[int] = Field(default=None, description="分页偏移量")
    # 单次 `limit` 最大为 1000；为 0 或不传时由接口按默认规则返回。
    limit: Optional[int] = Field(default=None, description="分页大小")


class GetViewsResponse(WeComBaseResponse):
    """查询视图响应体。"""

    total: Optional[int] = Field(default=None, description="总数量")
    has_more: Optional[bool] = Field(default=None, description="是否有下一页")
    next: Optional[int] = Field(default=None, description="下一页偏移量")
    views: Optional[List[View]] = Field(default=None, description="视图列表")
