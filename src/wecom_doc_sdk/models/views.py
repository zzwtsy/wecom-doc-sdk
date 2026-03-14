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
    value: List[str]


class NumberValue(WeComBaseModel):
    value: float


class BoolValue(WeComBaseModel):
    value: bool


class UserValue(WeComBaseModel):
    value: List[str]


class FilterDateTimeValue(WeComBaseModel):
    type: DateTimeType
    value: List[str]


class Condition(WeComBaseModel):
    """过滤条件。"""

    field_id: str
    field_type: Optional[FieldType] = None
    operator: Operator
    string_value: Optional[StringValue] = None
    number_value: Optional[NumberValue] = None
    bool_value: Optional[BoolValue] = None
    user_value: Optional[UserValue] = None
    date_time_value: Optional[FilterDateTimeValue] = None


class SortInfo(WeComBaseModel):
    field_id: str
    desc: Optional[bool] = None


class SortSpec(WeComBaseModel):
    sort_infos: Optional[List[SortInfo]] = None


class GroupInfo(WeComBaseModel):
    field_id: str
    desc: Optional[bool] = None


class GroupSpec(WeComBaseModel):
    groups: Optional[List[GroupInfo]] = None


class FilterSpec(WeComBaseModel):
    conjunction: Conjunction
    conditions: List[Condition]


class ViewColorCondition(WeComBaseModel):
    id: Optional[str] = None
    type: ViewColorConditionType
    color: ViewColor
    condition: Optional[Condition] = Field(
        default=None,
        validation_alias=AliasChoices("condition", "conditions"),
        serialization_alias="condition",
    )


class ViewColorConfig(WeComBaseModel):
    conditions: List[ViewColorCondition]


class ViewProperty(WeComBaseModel):
    auto_sort: Optional[bool] = None
    sort_spec: Optional[SortSpec] = None
    group_spec: Optional[GroupSpec] = None
    filter_spec: Optional[FilterSpec] = None
    is_field_stat_enabled: Optional[bool] = None
    field_visibility: Optional[Dict[str, bool]] = None
    frozen_field_count: Optional[int] = None
    color_config: Optional[ViewColorConfig] = None


class View(WeComBaseModel):
    view_id: str
    view_title: str
    view_type: ViewType
    property: Optional[ViewProperty] = None


class GanttViewProperty(WeComBaseModel):
    start_date_field_id: str
    end_date_field_id: str


class CalendarViewProperty(WeComBaseModel):
    start_date_field_id: str
    end_date_field_id: str


class AddViewRequest(WeComBaseModel):
    docid: str
    sheet_id: str
    view_title: str
    view_type: ViewType
    property_gantt: Optional[GanttViewProperty] = None
    property_calendar: Optional[CalendarViewProperty] = None


class AddViewResponse(WeComBaseResponse):
    view: Optional[View] = None


class DeleteViewsRequest(WeComBaseModel):
    docid: str
    sheet_id: str
    view_ids: List[str]


class DeleteViewsResponse(WeComBaseResponse):
    pass


class UpdateViewRequest(WeComBaseModel):
    docid: str
    sheet_id: str
    view_id: str
    view_title: Optional[str] = None
    property: Optional[ViewProperty] = None


class UpdateViewResponse(WeComBaseResponse):
    view: Optional[View] = None


class GetViewsRequest(WeComBaseModel):
    docid: str
    sheet_id: str
    view_ids: Optional[List[str]] = None
    offset: Optional[int] = None
    limit: Optional[int] = None


class GetViewsResponse(WeComBaseResponse):
    total: Optional[int] = None
    has_more: Optional[bool] = None
    next: Optional[int] = None
    views: Optional[List[View]] = None
