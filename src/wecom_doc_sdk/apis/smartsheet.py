from __future__ import annotations

import base64
from typing import Any, Type, TypeVar

from pydantic import BaseModel

from ..client import WeComClient
from ..exceptions import WeComRequestError
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
from ..models.uploads import InitFileUploadRequest, UploadFileRequest
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

WEDRIVE_SIMPLE_UPLOAD_LIMIT = 10 * 1024 * 1024
WEDRIVE_CHUNK_SIZE = 2 * 1024 * 1024
WEDRIVE_MAX_FILE_SIZE = 20 * 1024 * 1024 * 1024


def _left_rotate(value: int, shift: int) -> int:
    """执行 32 位左循环移位。"""

    return ((value << shift) | (value >> (32 - shift))) & 0xFFFFFFFF


def _process_sha1_chunk(
    chunk: bytes, h0: int, h1: int, h2: int, h3: int, h4: int
) -> tuple[int, int, int, int, int]:
    """处理单个 64 字节 sha1 数据块。"""

    words = [0] * 80
    for index in range(16):
        offset = index * 4
        words[index] = int.from_bytes(chunk[offset : offset + 4], "big")

    for index in range(16, 80):
        words[index] = _left_rotate(
            words[index - 3] ^ words[index - 8] ^ words[index - 14] ^ words[index - 16],
            1,
        )

    a, b, c, d, e = h0, h1, h2, h3, h4
    for index in range(80):
        if index < 20:
            f = (b & c) | ((~b) & d)
            k = 0x5A827999
        elif index < 40:
            f = b ^ c ^ d
            k = 0x6ED9EBA1
        elif index < 60:
            f = (b & c) | (b & d) | (c & d)
            k = 0x8F1BBCDC
        else:
            f = b ^ c ^ d
            k = 0xCA62C1D6

        temp = (_left_rotate(a, 5) + f + e + k + words[index]) & 0xFFFFFFFF
        a, b, c, d, e = temp, a, _left_rotate(b, 30), c, d

    return (
        (h0 + a) & 0xFFFFFFFF,
        (h1 + b) & 0xFFFFFFFF,
        (h2 + c) & 0xFFFFFFFF,
        (h3 + d) & 0xFFFFFFFF,
        (h4 + e) & 0xFFFFFFFF,
    )


class _SHA1Accumulator:
    """支持导出中间 state 的 sha1 计算器。

    企业微信分块上传要求非最后一块传入 sha1 的中间 state，而不是普通的最终 digest。
    Python 标准库不会暴露这个中间 state，这里按 sha1 规范补一个仅供内部使用的实现。
    """

    def __init__(self) -> None:
        self._state = (
            0x67452301,
            0xEFCDAB89,
            0x98BADCFE,
            0x10325476,
            0xC3D2E1F0,
        )
        self._unprocessed = b""
        self._message_byte_length = 0

    def update(self, data: bytes) -> None:
        """增量写入待计算内容。"""

        self._message_byte_length += len(data)
        buffer = self._unprocessed + data
        chunked_length = len(buffer) - (len(buffer) % 64)
        for offset in range(0, chunked_length, 64):
            self._state = _process_sha1_chunk(
                buffer[offset : offset + 64], *self._state
            )
        self._unprocessed = buffer[chunked_length:]

    def state_hexdigest(self) -> str:
        """返回当前中间 state 的十六进制表示。"""

        if self._unprocessed:
            raise ValueError("sha1 中间 state 仅能在 64 字节边界上导出")
        return "".join(f"{value:08x}" for value in self._state)

    def final_hexdigest(self) -> str:
        """返回当前累计内容的最终 sha1。"""

        h0, h1, h2, h3, h4 = self._state
        total_bits = self._message_byte_length * 8
        buffer = self._unprocessed + b"\x80"
        padding_length = (56 - (len(buffer) % 64)) % 64
        buffer += b"\x00" * padding_length
        buffer += total_bits.to_bytes(8, "big")

        for offset in range(0, len(buffer), 64):
            h0, h1, h2, h3, h4 = _process_sha1_chunk(
                buffer[offset : offset + 64], h0, h1, h2, h3, h4
            )
        return "".join(f"{value:08x}" for value in (h0, h1, h2, h3, h4))


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
        values = {
            field_key: [
                (
                    self._client.dump_model(attachment)
                    if isinstance(attachment, BaseModel)
                    else attachment
                )
                for attachment in attachments
            ]
        }
        request_payload = {
            "docid": docid,
            "sheet_id": sheet_id,
            "key_type": key_type.value,
            "records": [{"values": values}],
        }
        return self.add_records(request_payload)

    @staticmethod
    def _normalize_attachment_values(values: Any) -> list[dict[str, Any]]:
        """将附件字段值标准化为附件字典列表。"""

        if values is None:
            return []

        if not isinstance(values, list):
            raise ValueError("附件字段值必须为附件列表")

        normalized: list[dict[str, Any]] = []
        for item in values:
            if isinstance(item, CellAttachmentValue):
                normalized.append(item.model_dump(by_alias=True, exclude_none=True))
                continue

            if isinstance(item, dict):
                attachment = CellAttachmentValue.model_validate(item)
                normalized.append(
                    attachment.model_dump(by_alias=True, exclude_none=True)
                )
                continue

            raise ValueError("附件字段值必须是 CellAttachmentValue 或 dict")

        return normalized

    def _get_existing_attachment_values(
        self,
        *,
        docid: str,
        sheet_id: str,
        record_id: str,
        field_key: str,
        key_type: CellValueKeyType,
    ) -> list[dict[str, Any]]:
        """查询目标记录当前附件字段值。"""

        request_payload: dict[str, Any] = {
            "docid": docid,
            "sheet_id": sheet_id,
            "record_ids": [record_id],
            "key_type": key_type.value,
            "limit": 1,
        }

        if key_type == CellValueKeyType.CELL_VALUE_KEY_TYPE_FIELD_ID:
            request_payload["field_ids"] = [field_key]
        else:
            request_payload["field_titles"] = [field_key]

        response = self.get_records(request_payload)
        if not response.records:
            raise ValueError(f"未找到记录：{record_id}")

        record = response.records[0]
        if record.record_id != record_id:
            raise ValueError(
                f"记录ID不匹配：期望 {record_id}，实际 {record.record_id}"
            )

        values = record.values or {}
        if field_key not in values:
            return []
        return self._normalize_attachment_values(values.get(field_key))

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

        normalized_new_attachments = self._normalize_attachment_values(attachments)
        merged_attachments = normalized_new_attachments

        if append:
            existing_attachments = self._get_existing_attachment_values(
                docid=docid,
                sheet_id=sheet_id,
                record_id=record_id,
                field_key=field_key,
                key_type=key_type,
            )
            merged_attachments = existing_attachments + normalized_new_attachments

        request_payload = {
            "docid": docid,
            "sheet_id": sheet_id,
            "key_type": key_type.value,
            "records": [
                {
                    "record_id": record_id,
                    "values": {field_key: merged_attachments},
                }
            ],
        }
        return self.update_records(request_payload)

    def _build_attachment_payload(
        self,
        file_id: str,
        *,
        attachment_metadata: dict[str, Any] | CellAttachmentValue | None = None,
        base_attachment: dict[str, Any] | None = None,
    ) -> dict[str, Any]:
        """合并附件基础信息与调用方传入的元数据。"""

        attachment: dict[str, Any] = {"file_id": file_id}
        if base_attachment is not None:
            attachment.update(base_attachment)

        if attachment_metadata is None:
            return attachment

        if isinstance(attachment_metadata, BaseModel):
            metadata = self._client.dump_model(attachment_metadata)
        else:
            metadata = dict(attachment_metadata)

        reserved_keys = {"file_id", "file_url"}
        conflict_keys = sorted(reserved_keys.intersection(metadata.keys()))
        if conflict_keys:
            raise ValueError(
                "attachment_metadata 不能覆盖保留字段：" + ", ".join(conflict_keys)
            )
        attachment.update(metadata)
        return attachment

    def _append_share_url(self, attachment: dict[str, Any], file_id: str) -> None:
        """查询并写入附件访问链接。"""

        share_resp = self._client.uploads.share_file({"fileid": file_id})
        if not share_resp.share_url:
            raise WeComRequestError("获取分享链接成功但响应缺少 share_url")
        attachment["file_url"] = share_resp.share_url

    @staticmethod
    def _encode_file_content(file_bytes: bytes) -> str:
        """将文件内容编码为企业微信要求的 Base64 字符串。"""

        return base64.b64encode(file_bytes).decode("ascii")

    @staticmethod
    def _split_file_bytes(file_bytes: bytes) -> list[bytes]:
        """按微盘固定 2MB 大小切分文件内容。"""

        return [
            file_bytes[offset : offset + WEDRIVE_CHUNK_SIZE]
            for offset in range(0, len(file_bytes), WEDRIVE_CHUNK_SIZE)
        ]

    @classmethod
    def _calculate_block_sha(cls, chunks: list[bytes]) -> list[str]:
        """计算微盘分块上传所需的累积 sha1。"""

        digest = _SHA1Accumulator()
        block_sha: list[str] = []
        for index, chunk in enumerate(chunks, start=1):
            digest.update(chunk)
            if index == len(chunks):
                block_sha.append(digest.final_hexdigest())
            else:
                block_sha.append(digest.state_hexdigest())
        return block_sha

    @staticmethod
    def _guess_file_ext(file_name: str) -> str | None:
        """从文件名推导附件字段所需的扩展名。"""

        if "." not in file_name:
            return None
        suffix = file_name.rsplit(".", 1)[-1].strip()
        return suffix.upper() if suffix else None

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

        file_size = len(file_bytes)
        if file_size > WEDRIVE_MAX_FILE_SIZE:
            raise ValueError("文件大小不能超过 20G")

        target_payload = {
            "spaceid": spaceid,
            "fatherid": fatherid,
            "selected_ticket": selected_ticket,
        }

        if file_size <= WEDRIVE_SIMPLE_UPLOAD_LIMIT:
            upload_req = UploadFileRequest.model_validate(
                {
                    **target_payload,
                    "file_name": file_name,
                    "file_base64_content": self._encode_file_content(file_bytes),
                }
            )
            upload_resp = self._client.uploads.upload_file(upload_req)
            if not upload_resp.fileid:
                raise WeComRequestError("上传文件成功但响应缺少 fileid")
            return upload_resp.fileid

        chunks = self._split_file_bytes(file_bytes)
        init_req = InitFileUploadRequest.model_validate(
            {
                **target_payload,
                "file_name": file_name,
                "size": file_size,
                "block_sha": self._calculate_block_sha(chunks),
            }
        )
        init_resp = self._client.uploads.init_file_upload(init_req)
        if init_resp.hit_exist:
            if not init_resp.fileid:
                raise WeComRequestError("分块上传初始化命中秒传但响应缺少 fileid")
            return init_resp.fileid

        if not init_resp.upload_key:
            raise WeComRequestError("分块上传初始化成功但响应缺少 upload_key")

        for index, chunk in enumerate(chunks, start=1):
            self._client.uploads.upload_file_part(
                {
                    "upload_key": init_resp.upload_key,
                    "index": index,
                    "file_base64_content": self._encode_file_content(chunk),
                }
            )

        finish_resp = self._client.uploads.finish_file_upload(
            {"upload_key": init_resp.upload_key}
        )
        if not finish_resp.fileid:
            raise WeComRequestError("分块上传完成但响应缺少 fileid")
        return finish_resp.fileid

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
        upload_req = self._ensure_model(UploadFileRequest, upload_request)
        upload_resp = self._client.uploads.upload_file(upload_req)
        file_id = upload_resp.fileid
        if not file_id:
            raise WeComRequestError("上传文件成功但响应缺少 fileid")

        attachment = self._build_attachment_payload(
            file_id, attachment_metadata=attachment_metadata
        )

        if share_link:
            self._append_share_url(attachment, file_id)

        return self.add_records_with_attachment(
            docid=docid,
            sheet_id=sheet_id,
            field_key=field_key,
            attachments=[attachment],
            key_type=key_type,
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

        file_id = self._upload_file_bytes(
            file_name=file_name,
            file_bytes=file_bytes,
            spaceid=spaceid,
            fatherid=fatherid,
            selected_ticket=selected_ticket,
        )

        base_attachment: dict[str, Any] = {
            "name": file_name,
            "size": len(file_bytes),
            "doc_type": 2,
            "file_type": "Wedrive",
        }
        file_ext = self._guess_file_ext(file_name)
        if file_ext:
            base_attachment["file_ext"] = file_ext

        attachment = self._build_attachment_payload(
            file_id,
            attachment_metadata=attachment_metadata,
            base_attachment=base_attachment,
        )
        if share_link:
            self._append_share_url(attachment, file_id)

        return self.add_records_with_attachment(
            docid=docid,
            sheet_id=sheet_id,
            field_key=field_key,
            attachments=[attachment],
            key_type=key_type,
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

        file_id = self._upload_file_bytes(
            file_name=file_name,
            file_bytes=file_bytes,
            spaceid=spaceid,
            fatherid=fatherid,
            selected_ticket=selected_ticket,
        )

        base_attachment: dict[str, Any] = {
            "name": file_name,
            "size": len(file_bytes),
            "doc_type": 2,
            "file_type": "Wedrive",
        }
        file_ext = self._guess_file_ext(file_name)
        if file_ext:
            base_attachment["file_ext"] = file_ext

        attachment = self._build_attachment_payload(
            file_id,
            attachment_metadata=attachment_metadata,
            base_attachment=base_attachment,
        )
        if share_link:
            self._append_share_url(attachment, file_id)

        return self.update_record_with_attachment(
            docid=docid,
            sheet_id=sheet_id,
            record_id=record_id,
            field_key=field_key,
            attachments=[attachment],
            key_type=key_type,
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
