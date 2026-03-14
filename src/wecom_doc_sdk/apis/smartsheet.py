from __future__ import annotations

from typing import Any, Type, TypeVar

from pydantic import BaseModel

from ..client import WeComClient
from ..models.fields import (
    AddFieldsRequest,
    AddFieldsResponse,
    DeleteFieldsRequest,
    DeleteFieldsResponse,
    GetFieldsRequest,
    GetFieldsResponse,
    UpdateFieldsRequest,
    UpdateFieldsResponse,
)
from ..models.groups import (
    AddFieldGroupRequest,
    AddFieldGroupResponse,
    DeleteFieldGroupsRequest,
    DeleteFieldGroupsResponse,
    GetFieldGroupsRequest,
    GetFieldGroupsResponse,
    UpdateFieldGroupRequest,
    UpdateFieldGroupResponse,
)
from ..models.records import (
    AddRecordsRequest,
    AddRecordsResponse,
    DeleteRecordsRequest,
    DeleteRecordsResponse,
    GetRecordsRequest,
    GetRecordsResponse,
    UpdateRecordsRequest,
    UpdateRecordsResponse,
)
from ..models.sheets import (
    AddSheetRequest,
    AddSheetResponse,
    DeleteSheetRequest,
    DeleteSheetResponse,
    GetSheetRequest,
    GetSheetResponse,
    UpdateSheetRequest,
    UpdateSheetResponse,
)
from ..models.views import (
    AddViewRequest,
    AddViewResponse,
    DeleteViewsRequest,
    DeleteViewsResponse,
    GetViewsRequest,
    GetViewsResponse,
    UpdateViewRequest,
    UpdateViewResponse,
)

TModel = TypeVar("TModel", bound=BaseModel)


class SmartSheetAPI:
    """管理智能表格内容相关接口封装。"""

    def __init__(self, client: WeComClient) -> None:
        self._client = client

    @staticmethod
    def _ensure_model(model_cls: Type[TModel], payload: Any) -> TModel:
        if isinstance(payload, model_cls):
            return payload
        return model_cls.model_validate(payload)

    # --- 子表 ---
    def add_sheet(self, request: AddSheetRequest | dict[str, Any]) -> AddSheetResponse:
        """在文档的指定位置新增一个智能表子表。

        新建子表初始不包含视图、记录和字段，后续需再调用对应接口补充内容。
        """
        req = self._ensure_model(AddSheetRequest, request)
        data = self._client.request_json(
            "POST",
            "/cgi-bin/wedoc/smartsheet/add_sheet",
            json=self._client.dump_model(req),
        )
        return AddSheetResponse.model_validate(data)

    def delete_sheet(
        self, request: DeleteSheetRequest | dict[str, Any]
    ) -> DeleteSheetResponse:
        """删除在线表格中的指定子表。"""
        req = self._ensure_model(DeleteSheetRequest, request)
        data = self._client.request_json(
            "POST",
            "/cgi-bin/wedoc/smartsheet/delete_sheet",
            json=self._client.dump_model(req),
        )
        return DeleteSheetResponse.model_validate(data)

    def update_sheet(
        self, request: UpdateSheetRequest | dict[str, Any]
    ) -> UpdateSheetResponse:
        """更新子表信息，当前主要用于修改子表标题。"""
        req = self._ensure_model(UpdateSheetRequest, request)
        data = self._client.request_json(
            "POST",
            "/cgi-bin/wedoc/smartsheet/update_sheet",
            json=self._client.dump_model(req),
        )
        return UpdateSheetResponse.model_validate(data)

    def get_sheet(self, request: GetSheetRequest | dict[str, Any]) -> GetSheetResponse:
        """查询文档下的子表信息。"""
        req = self._ensure_model(GetSheetRequest, request)
        data = self._client.request_json(
            "POST",
            "/cgi-bin/wedoc/smartsheet/get_sheet",
            json=self._client.dump_model(req),
        )
        return GetSheetResponse.model_validate(data)

    # --- 视图 ---
    def add_view(self, request: AddViewRequest | dict[str, Any]) -> AddViewResponse:
        """在子表中新增视图。

        单表最多允许 200 个视图；添加甘特图或日历视图时需传入对应属性。
        """
        req = self._ensure_model(AddViewRequest, request)
        data = self._client.request_json(
            "POST",
            "/cgi-bin/wedoc/smartsheet/add_view",
            json=self._client.dump_model(req),
        )
        return AddViewResponse.model_validate(data)

    def delete_views(
        self, request: DeleteViewsRequest | dict[str, Any]
    ) -> DeleteViewsResponse:
        """批量删除子表中的一个或多个视图。"""
        req = self._ensure_model(DeleteViewsRequest, request)
        data = self._client.request_json(
            "POST",
            "/cgi-bin/wedoc/smartsheet/delete_views",
            json=self._client.dump_model(req),
        )
        return DeleteViewsResponse.model_validate(data)

    def update_view(
        self, request: UpdateViewRequest | dict[str, Any]
    ) -> UpdateViewResponse:
        """更新视图标题或视图属性。

        支持调整排序、过滤、分组、字段显示、冻结列和填色等配置。
        """
        req = self._ensure_model(UpdateViewRequest, request)
        data = self._client.request_json(
            "POST",
            "/cgi-bin/wedoc/smartsheet/update_view",
            json=self._client.dump_model(req),
        )
        return UpdateViewResponse.model_validate(data)

    def get_views(self, request: GetViewsRequest | dict[str, Any]) -> GetViewsResponse:
        """获取子表下全部视图信息。"""
        req = self._ensure_model(GetViewsRequest, request)
        data = self._client.request_json(
            "POST",
            "/cgi-bin/wedoc/smartsheet/get_views",
            json=self._client.dump_model(req),
        )
        return GetViewsResponse.model_validate(data)

    # --- 字段 ---
    def add_fields(
        self, request: AddFieldsRequest | dict[str, Any]
    ) -> AddFieldsResponse:
        """在子表中新增一个或多个字段。

        单表最多允许 150 个字段，字段类型与字段属性必须严格匹配。
        """
        req = self._ensure_model(AddFieldsRequest, request)
        data = self._client.request_json(
            "POST",
            "/cgi-bin/wedoc/smartsheet/add_fields",
            json=self._client.dump_model(req),
        )
        return AddFieldsResponse.model_validate(data)

    def delete_fields(
        self, request: DeleteFieldsRequest | dict[str, Any]
    ) -> DeleteFieldsResponse:
        """批量删除子表中的字段。"""
        req = self._ensure_model(DeleteFieldsRequest, request)
        data = self._client.request_json(
            "POST",
            "/cgi-bin/wedoc/smartsheet/delete_fields",
            json=self._client.dump_model(req),
        )
        return DeleteFieldsResponse.model_validate(data)

    def update_fields(
        self, request: UpdateFieldsRequest | dict[str, Any]
    ) -> UpdateFieldsResponse:
        """更新字段标题或字段属性。

        该接口不支持修改字段类型；更新时至少应提供待变更的标题或字段属性。
        """
        req = self._ensure_model(UpdateFieldsRequest, request)
        data = self._client.request_json(
            "POST",
            "/cgi-bin/wedoc/smartsheet/update_fields",
            json=self._client.dump_model(req),
        )
        return UpdateFieldsResponse.model_validate(data)

    def get_fields(
        self, request: GetFieldsRequest | dict[str, Any]
    ) -> GetFieldsResponse:
        """查询子表字段信息。

        支持按字段 ID、字段标题或分页方式获取，单次 `limit` 最大为 1000。
        """
        req = self._ensure_model(GetFieldsRequest, request)
        data = self._client.request_json(
            "POST",
            "/cgi-bin/wedoc/smartsheet/get_fields",
            json=self._client.dump_model(req),
        )
        return GetFieldsResponse.model_validate(data)

    # --- 记录 ---
    def add_records(
        self, request: AddRecordsRequest | dict[str, Any]
    ) -> AddRecordsResponse:
        """在子表中新增一行或多行记录。

        单次添加建议控制在 500 行内，且不能写入创建时间、最后编辑时间、创建人、
        最后编辑人字段。
        """
        req = self._ensure_model(AddRecordsRequest, request)
        data = self._client.request_json(
            "POST",
            "/cgi-bin/wedoc/smartsheet/add_records",
            json=self._client.dump_model(req),
        )
        return AddRecordsResponse.model_validate(data)

    def delete_records(
        self, request: DeleteRecordsRequest | dict[str, Any]
    ) -> DeleteRecordsResponse:
        """批量删除子表中的记录，单次删除建议控制在 500 行内。"""
        req = self._ensure_model(DeleteRecordsRequest, request)
        data = self._client.request_json(
            "POST",
            "/cgi-bin/wedoc/smartsheet/delete_records",
            json=self._client.dump_model(req),
        )
        return DeleteRecordsResponse.model_validate(data)

    def update_records(
        self, request: UpdateRecordsRequest | dict[str, Any]
    ) -> UpdateRecordsResponse:
        """更新子表中的一行或多行记录。

        单次更新建议控制在 500 行内，且不能更新创建时间、最后编辑时间、创建人、
        最后编辑人字段。
        """
        req = self._ensure_model(UpdateRecordsRequest, request)
        data = self._client.request_json(
            "POST",
            "/cgi-bin/wedoc/smartsheet/update_records",
            json=self._client.dump_model(req),
        )
        return UpdateRecordsResponse.model_validate(data)

    def get_records(
        self, request: GetRecordsRequest | dict[str, Any]
    ) -> GetRecordsResponse:
        """查询子表记录信息。

        支持全量查询、按记录或字段筛选以及排序；`filter_spec` 与 `sort` 不能同时使用，
        单次 `limit` 最大为 1000。
        """
        req = self._ensure_model(GetRecordsRequest, request)
        data = self._client.request_json(
            "POST",
            "/cgi-bin/wedoc/smartsheet/get_records",
            json=self._client.dump_model(req),
        )
        return GetRecordsResponse.model_validate(data)

    # --- 编组 ---
    def add_field_group(
        self, request: AddFieldGroupRequest | dict[str, Any]
    ) -> AddFieldGroupResponse:
        """在子表中新增编组。

        单表最多允许 150 个编组，每个编组最多 150 个字段，且字段只能同时属于一个编组。
        """
        req = self._ensure_model(AddFieldGroupRequest, request)
        data = self._client.request_json(
            "POST",
            "/cgi-bin/wedoc/smartsheet/add_field_group",
            json=self._client.dump_model(req),
        )
        return AddFieldGroupResponse.model_validate(data)

    def update_field_group(
        self, request: UpdateFieldGroupRequest | dict[str, Any]
    ) -> UpdateFieldGroupResponse:
        """更新已有编组的名称或字段成员。

        编组名称不能与已有编组重复，字段仍只能同时属于一个编组。
        """
        req = self._ensure_model(UpdateFieldGroupRequest, request)
        data = self._client.request_json(
            "POST",
            "/cgi-bin/wedoc/smartsheet/update_field_group",
            json=self._client.dump_model(req),
        )
        return UpdateFieldGroupResponse.model_validate(data)

    def delete_field_groups(
        self, request: DeleteFieldGroupsRequest | dict[str, Any]
    ) -> DeleteFieldGroupsResponse:
        """批量删除子表中的一个或多个编组。"""
        req = self._ensure_model(DeleteFieldGroupsRequest, request)
        data = self._client.request_json(
            "POST",
            "/cgi-bin/wedoc/smartsheet/delete_field_groups",
            json=self._client.dump_model(req),
        )
        return DeleteFieldGroupsResponse.model_validate(data)

    def get_field_groups(
        self, request: GetFieldGroupsRequest | dict[str, Any]
    ) -> GetFieldGroupsResponse:
        """获取子表下已有的编组信息。"""
        req = self._ensure_model(GetFieldGroupsRequest, request)
        data = self._client.request_json(
            "POST",
            "/cgi-bin/wedoc/smartsheet/get_field_groups",
            json=self._client.dump_model(req),
        )
        return GetFieldGroupsResponse.model_validate(data)
