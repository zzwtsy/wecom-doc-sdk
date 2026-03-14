from __future__ import annotations

from typing import List, Optional

from .common import WeComBaseModel, WeComBaseResponse


class FieldGroupChild(WeComBaseModel):
    field_id: str


class FieldGroup(WeComBaseModel):
    field_group_id: Optional[str] = None
    name: Optional[str] = None
    children: Optional[List[FieldGroupChild]] = None


class AddFieldGroupRequest(WeComBaseModel):
    docid: str
    sheet_id: str
    name: str
    children: Optional[List[FieldGroupChild]] = None


class AddFieldGroupResponse(WeComBaseResponse):
    field_group: Optional[FieldGroup] = None


class UpdateFieldGroupRequest(WeComBaseModel):
    docid: str
    sheet_id: str
    field_group_id: str
    name: Optional[str] = None
    children: Optional[List[FieldGroupChild]] = None


class UpdateFieldGroupResponse(WeComBaseResponse):
    field_group: Optional[FieldGroup] = None


class DeleteFieldGroupsRequest(WeComBaseModel):
    docid: str
    sheet_id: str
    field_group_ids: List[str]


class DeleteFieldGroupsResponse(WeComBaseResponse):
    pass


class GetFieldGroupsRequest(WeComBaseModel):
    docid: str
    sheet_id: str
    offset: Optional[int] = None
    limit: Optional[int] = None


class GetFieldGroupsResponse(WeComBaseResponse):
    total: Optional[int] = None
    has_more: Optional[bool] = None
    next: Optional[int] = None
    field_groups: Optional[List[FieldGroup]] = None
