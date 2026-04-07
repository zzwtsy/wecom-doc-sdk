from __future__ import annotations

from typing import List, Optional

from pydantic import Field

from .common import WeComBaseModel, WeComBaseResponse


class FieldGroupChild(WeComBaseModel):
    """编组内的字段引用。"""

    # 被编入当前分组的字段 ID。
    field_id: str = Field(description="字段 ID")


class FieldGroup(WeComBaseModel):
    """字段编组信息。"""

    field_group_id: Optional[str] = Field(default=None, description="编组 ID")
    # 编组名称在同一子表中应保持唯一。
    name: Optional[str] = Field(default=None, description="编组名称")
    # 编组内字段列表；同一个字段只能属于一个编组。
    children: Optional[List[FieldGroupChild]] = Field(
        default=None, description="编组内字段列表"
    )


class AddFieldGroupRequest(WeComBaseModel):
    """添加编组请求体。"""

    docid: str = Field(description="文档 ID")
    sheet_id: str = Field(description="子表 ID")
    # 编组名称不能与同一子表中的已有名称重复。
    name: str = Field(description="编组名称")
    children: Optional[List[FieldGroupChild]] = Field(
        default=None, description="编组字段列表"
    )


class AddFieldGroupResponse(WeComBaseResponse):
    """添加编组响应体。"""

    field_group: Optional[FieldGroup] = Field(
        default=None, description="新增后的编组信息"
    )


class UpdateFieldGroupRequest(WeComBaseModel):
    """更新编组请求体。"""

    docid: str = Field(description="文档 ID")
    sheet_id: str = Field(description="子表 ID")
    field_group_id: str = Field(description="待更新编组 ID")
    name: Optional[str] = Field(default=None, description="更新后的编组名称")
    children: Optional[List[FieldGroupChild]] = Field(
        default=None, description="更新后的编组字段列表"
    )


class UpdateFieldGroupResponse(WeComBaseResponse):
    """更新编组响应体。"""

    field_group: Optional[FieldGroup] = Field(
        default=None, description="更新后的编组信息"
    )


class DeleteFieldGroupsRequest(WeComBaseModel):
    """删除编组请求体。"""

    docid: str = Field(description="文档 ID")
    sheet_id: str = Field(description="子表 ID")
    field_group_ids: List[str] = Field(description="待删除编组 ID 列表")


class DeleteFieldGroupsResponse(WeComBaseResponse):
    """删除编组响应体。"""

    pass


class GetFieldGroupsRequest(WeComBaseModel):
    """查询编组请求体。"""

    docid: str = Field(description="文档 ID")
    sheet_id: str = Field(description="子表 ID")
    # 分页偏移量，初始值通常为 0。
    offset: Optional[int] = Field(default=None, description="分页偏移量")
    # 每页条数；用于控制批量拉取编组列表。
    limit: Optional[int] = Field(default=None, description="分页大小")


class GetFieldGroupsResponse(WeComBaseResponse):
    """查询编组响应体。"""

    total: Optional[int] = Field(default=None, description="总数量")
    has_more: Optional[bool] = Field(default=None, description="是否有下一页")
    next: Optional[int] = Field(default=None, description="下一页偏移量")
    field_groups: Optional[List[FieldGroup]] = Field(
        default=None, description="编组列表"
    )
