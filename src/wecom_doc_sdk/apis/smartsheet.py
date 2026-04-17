from __future__ import annotations

from typing import Any, Type, TypeVar

from pydantic import BaseModel

from ..client import WeComClient
from ..models.enums import CellValueKeyType
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
    CellAttachmentValue,
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
from ..models.uploads import UploadFileRequest
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
from .smartsheet_attachment import SmartSheetAttachmentHelper
from .smartsheet_upload import (
    WEDRIVE_CHUNK_SIZE as DEFAULT_WEDRIVE_CHUNK_SIZE,
)
from .smartsheet_upload import (
    WEDRIVE_MAX_FILE_SIZE as DEFAULT_WEDRIVE_MAX_FILE_SIZE,
)
from .smartsheet_upload import (
    WEDRIVE_SIMPLE_UPLOAD_LIMIT as DEFAULT_WEDRIVE_SIMPLE_UPLOAD_LIMIT,
)
from .smartsheet_upload import (
    SmartSheetUploadHelper,
)

TModel = TypeVar("TModel", bound=BaseModel)

WEDRIVE_SIMPLE_UPLOAD_LIMIT = DEFAULT_WEDRIVE_SIMPLE_UPLOAD_LIMIT
WEDRIVE_CHUNK_SIZE = DEFAULT_WEDRIVE_CHUNK_SIZE
WEDRIVE_MAX_FILE_SIZE = DEFAULT_WEDRIVE_MAX_FILE_SIZE


class SmartSheetAPI:
    """管理智能表格内容相关接口封装。"""

    def __init__(self, client: WeComClient) -> None:
        self._client = client
        self._upload_helper = SmartSheetUploadHelper(client)
        self._attachment_helper = SmartSheetAttachmentHelper(
            client,
            add_records=self.add_records,
            update_records=self.update_records,
            get_records=self.get_records,
            upload_file_bytes=self._upload_file_bytes,
        )

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

    def add_records_with_attachment(
        self,
        docid: str,
        sheet_id: str,
        field_key: str,
        attachments: list[CellAttachmentValue | dict[str, Any]],
        *,
        key_type: CellValueKeyType = CellValueKeyType.CELL_VALUE_KEY_TYPE_FIELD_ID,
    ) -> AddRecordsResponse:
        """新增包含附件字段的记录。

        附件字段需要传入已有文件的 metadata，例如 file_id、file_url、name、size、
        file_ext 等。该方法仅封装了记录结构构造，文件本身应先通过上传接口获取。
        """
        return self._attachment_helper.add_records_with_attachment(
            docid=docid,
            sheet_id=sheet_id,
            field_key=field_key,
            attachments=attachments,
            key_type=key_type,
        )

    def update_record_with_attachment(
        self,
        docid: str,
        sheet_id: str,
        record_id: str,
        field_key: str,
        attachments: list[CellAttachmentValue | dict[str, Any]],
        *,
        key_type: CellValueKeyType = CellValueKeyType.CELL_VALUE_KEY_TYPE_FIELD_ID,
        append: bool = False,
    ) -> UpdateRecordsResponse:
        """
        Args:
            docid: 文档 ID。
            sheet_id: 子表 ID。
            record_id: 目标记录 ID。
            field_key: 附件字段的键。其含义由 ``key_type`` 决定；当
                ``key_type`` 为字段 ID 时应传入字段 ID，否则应传入字段标题。
            attachments: 要写入的附件列表，可为 ``CellAttachmentValue`` 或与其
                结构兼容的字典。
            key_type: 指定 ``field_key`` 的类型，用于决定请求中按字段 ID 还是
                字段标题定位附件字段。
            append: 是否在保留现有附件的基础上追加新附件。为 ``True`` 时，会先
                查询记录当前附件并与 ``attachments`` 合并后再更新；该流程为先读
                后写，非原子操作，并发场景下可能覆盖其他更新。

        Returns:
            UpdateRecordsResponse: 更新记录接口的响应结果。

        Raises:
            ValueError: 附件值结构不合法、目标记录不存在，或 `append=True`
                时现有字段值不是附件列表。
            WeComAPIError: 企业微信接口返回业务错误时抛出。
            WeComRequestError: 请求企业微信接口失败时抛出。

        `append=True` 时会先查询记录现有附件并与新附件合并后再更新。
        """

        return self._attachment_helper.update_record_with_attachment(
            docid=docid,
            sheet_id=sheet_id,
            record_id=record_id,
            field_key=field_key,
            attachments=attachments,
            key_type=key_type,
            append=append,
        )

    def _upload_file_bytes(
        self,
        *,
        file_name: str,
        file_bytes: bytes,
        spaceid: str | None = None,
        fatherid: str | None = None,
        selected_ticket: str | None = None,
    ) -> str:
        """根据文件大小选择微盘直传或分块上传。"""

        return self._upload_helper.upload_file_bytes(
            file_name=file_name,
            file_bytes=file_bytes,
            spaceid=spaceid,
            fatherid=fatherid,
            selected_ticket=selected_ticket,
            simple_upload_limit=WEDRIVE_SIMPLE_UPLOAD_LIMIT,
            chunk_size=WEDRIVE_CHUNK_SIZE,
            max_file_size=WEDRIVE_MAX_FILE_SIZE,
        )

    def upload_file_and_add_attachment_record(
        self,
        docid: str,
        sheet_id: str,
        field_key: str,
        upload_request: UploadFileRequest | dict[str, Any],
        *,
        attachment_metadata: dict[str, Any] | CellAttachmentValue | None = None,
        key_type: CellValueKeyType = CellValueKeyType.CELL_VALUE_KEY_TYPE_FIELD_ID,
        share_link: bool = False,
    ) -> AddRecordsResponse:
        """上传文件到微盘并新增包含附件字段的记录。"""
        return self._attachment_helper.upload_file_and_add_attachment_record(
            docid=docid,
            sheet_id=sheet_id,
            field_key=field_key,
            upload_request=upload_request,
            attachment_metadata=attachment_metadata,
            key_type=key_type,
            share_link=share_link,
        )

    def upload_bytes_and_add_attachment_record(
        self,
        docid: str,
        sheet_id: str,
        field_key: str,
        file_name: str,
        file_bytes: bytes,
        *,
        spaceid: str | None = None,
        fatherid: str | None = None,
        selected_ticket: str | None = None,
        attachment_metadata: dict[str, Any] | CellAttachmentValue | None = None,
        key_type: CellValueKeyType = CellValueKeyType.CELL_VALUE_KEY_TYPE_FIELD_ID,
        share_link: bool = True,
    ) -> AddRecordsResponse:
        """根据文件字节内容上传到微盘，并写入智能表格附件字段。"""
        return self._attachment_helper.upload_bytes_and_add_attachment_record(
            docid=docid,
            sheet_id=sheet_id,
            field_key=field_key,
            file_name=file_name,
            file_bytes=file_bytes,
            spaceid=spaceid,
            fatherid=fatherid,
            selected_ticket=selected_ticket,
            attachment_metadata=attachment_metadata,
            key_type=key_type,
            share_link=share_link,
        )

    def upload_bytes_and_update_attachment_record(
        self,
        docid: str,
        sheet_id: str,
        record_id: str,
        field_key: str,
        file_name: str,
        file_bytes: bytes,
        *,
        spaceid: str | None = None,
        fatherid: str | None = None,
        selected_ticket: str | None = None,
        attachment_metadata: dict[str, Any] | CellAttachmentValue | None = None,
        key_type: CellValueKeyType = CellValueKeyType.CELL_VALUE_KEY_TYPE_FIELD_ID,
        share_link: bool = True,
        append: bool = False,
    ) -> UpdateRecordsResponse:
        """根据文件字节内容上传到微盘，并更新已有记录的附件字段。

        该方法会先将 `file_bytes` 上传到微盘，随后构造智能表格附件字段所需的
        附件对象，并调用记录更新接口写入指定记录。

        Args:
            docid: 智能表格文档 ID。
            sheet_id: 子表 ID。
            record_id: 需要更新的记录 ID。
            field_key: 附件字段的字段标识；其解释方式由 `key_type` 决定。
            file_name: 上传文件名，同时用于附件默认名称和扩展名推断。
            file_bytes: 要上传的文件二进制内容。
            spaceid: 微盘空间 ID。未提供时由底层上传接口使用其默认行为。
            fatherid: 微盘父目录 ID。未提供时由底层上传接口使用其默认行为。
            selected_ticket: 上传文件时使用的凭证。未提供时由底层上传接口决定。
            attachment_metadata: 额外的附件元数据，可为 `dict`、`CellAttachmentValue`
                或 `None`。提供后会与默认附件信息合并；其中的字段可覆盖默认值，
                例如名称、大小、文件扩展名或其他附件属性。
            key_type: `field_key` 的类型，默认按字段 ID 解析。
            share_link: 是否在附件数据中追加分享链接信息。为 `True` 时会调用
                分享链接补充逻辑，使生成的附件 payload 包含可分享 URL；为 `False`
                时仅写入基础附件信息。
            append: 是否以追加模式更新附件字段。`False` 表示使用传入附件列表更新
                目标字段；`True` 表示在底层更新逻辑支持时，将新附件追加到已有附件。
                需要注意，此流程不是原子操作：文件上传成功后，后续记录更新仍可能失败，
                因而在 `append=True` 时尤其要由调用方自行处理重试、幂等和清理问题。

        Returns:
            UpdateRecordsResponse: 更新记录后的接口响应。

        Raises:
            ValueError: 上传目标参数、附件元数据或追加模式下的附件字段值不满足
                helper 约束时抛出。
            WeComAPIError: 企业微信接口返回业务错误时抛出。
            WeComRequestError: 文件上传、分享链接补充或记录更新失败时抛出。若异常
                发生在上传成功之后，微盘中的文件可能已经存在，但记录字段尚未更新。
        """

        return self._attachment_helper.upload_bytes_and_update_attachment_record(
            docid=docid,
            sheet_id=sheet_id,
            record_id=record_id,
            field_key=field_key,
            file_name=file_name,
            file_bytes=file_bytes,
            spaceid=spaceid,
            fatherid=fatherid,
            selected_ticket=selected_ticket,
            attachment_metadata=attachment_metadata,
            key_type=key_type,
            share_link=share_link,
            append=append,
        )

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
