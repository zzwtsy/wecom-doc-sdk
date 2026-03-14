from __future__ import annotations

from typing import List, Optional

from .common import WeComBaseModel, WeComBaseResponse


class FieldGroupChild(WeComBaseModel):
    """编组内的字段引用。"""

    # 被编入当前分组的字段 ID。
    field_id: str


class FieldGroup(WeComBaseModel):
    """字段编组信息。"""

    field_group_id: Optional[str] = None
    # 编组名称在同一子表中应保持唯一。
    name: Optional[str] = None
    # 编组内字段列表；同一个字段只能属于一个编组。
    children: Optional[List[FieldGroupChild]] = None


class AddFieldGroupRequest(WeComBaseModel):
    """添加编组请求体。"""

    docid: str
    sheet_id: str
    # 编组名称不能与同一子表中的已有名称重复。
    name: str
    children: Optional[List[FieldGroupChild]] = None


class AddFieldGroupResponse(WeComBaseResponse):
    """添加编组响应体。"""

    field_group: Optional[FieldGroup] = None


class UpdateFieldGroupRequest(WeComBaseModel):
    """更新编组请求体。"""

    docid: str
    sheet_id: str
    field_group_id: str
    name: Optional[str] = None
    children: Optional[List[FieldGroupChild]] = None


class UpdateFieldGroupResponse(WeComBaseResponse):
    """更新编组响应体。"""

    field_group: Optional[FieldGroup] = None


class DeleteFieldGroupsRequest(WeComBaseModel):
    """删除编组请求体。"""

    docid: str
    sheet_id: str
    field_group_ids: List[str]


class DeleteFieldGroupsResponse(WeComBaseResponse):
    """删除编组响应体。"""

    pass


class GetFieldGroupsRequest(WeComBaseModel):
    """查询编组请求体。"""

    docid: str
    sheet_id: str
    # 分页偏移量，初始值通常为 0。
    offset: Optional[int] = None
    # 每页条数；用于控制批量拉取编组列表。
    limit: Optional[int] = None


class GetFieldGroupsResponse(WeComBaseResponse):
    """查询编组响应体。"""

    total: Optional[int] = None
    has_more: Optional[bool] = None
    next: Optional[int] = None
    field_groups: Optional[List[FieldGroup]] = None
