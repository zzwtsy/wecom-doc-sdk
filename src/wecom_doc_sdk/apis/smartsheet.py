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
        req = self._ensure_model(UpdateSheetRequest, request)
        data = self._client.request_json(
            "POST",
            "/cgi-bin/wedoc/smartsheet/update_sheet",
            json=self._client.dump_model(req),
        )
        return UpdateSheetResponse.model_validate(data)

    def get_sheet(self, request: GetSheetRequest | dict[str, Any]) -> GetSheetResponse:
        req = self._ensure_model(GetSheetRequest, request)
        data = self._client.request_json(
            "POST",
            "/cgi-bin/wedoc/smartsheet/get_sheet",
            json=self._client.dump_model(req),
        )
        return GetSheetResponse.model_validate(data)

    # --- 视图 ---
    def add_view(self, request: AddViewRequest | dict[str, Any]) -> AddViewResponse:
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
        req = self._ensure_model(UpdateViewRequest, request)
        data = self._client.request_json(
            "POST",
            "/cgi-bin/wedoc/smartsheet/update_view",
            json=self._client.dump_model(req),
        )
        return UpdateViewResponse.model_validate(data)

    def get_views(self, request: GetViewsRequest | dict[str, Any]) -> GetViewsResponse:
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
        req = self._ensure_model(GetFieldGroupsRequest, request)
        data = self._client.request_json(
            "POST",
            "/cgi-bin/wedoc/smartsheet/get_field_groups",
            json=self._client.dump_model(req),
        )
        return GetFieldGroupsResponse.model_validate(data)
