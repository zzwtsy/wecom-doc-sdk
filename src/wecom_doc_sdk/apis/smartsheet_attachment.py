from __future__ import annotations

from collections.abc import Callable
from typing import Any

from pydantic import BaseModel

from ..client import WeComClient
from ..exceptions import WeComRequestError
from ..models.enums import CellValueKeyType
from ..models.records import (
    AddRecordsRequest,
    AddRecordsResponse,
    CellAttachmentValue,
    GetRecordsRequest,
    GetRecordsResponse,
    UpdateRecordsRequest,
    UpdateRecordsResponse,
)
from ..models.uploads import UploadFileRequest

AddRecordsCallable = Callable[
    [AddRecordsRequest | dict[str, Any]],
    AddRecordsResponse,
]
UpdateRecordsCallable = Callable[
    [UpdateRecordsRequest | dict[str, Any]],
    UpdateRecordsResponse,
]
GetRecordsCallable = Callable[
    [GetRecordsRequest | dict[str, Any]],
    GetRecordsResponse,
]
UploadFileBytesCallable = Callable[..., str]


class SmartSheetAttachmentHelper:
    """封装智能表格附件字段的构造、上传编排与追加更新逻辑。"""

    def __init__(
        self,
        client: WeComClient,
        *,
        add_records: AddRecordsCallable,
        update_records: UpdateRecordsCallable,
        get_records: GetRecordsCallable,
        upload_file_bytes: UploadFileBytesCallable,
    ) -> None:
        self._client = client
        self._add_records = add_records
        self._update_records = update_records
        self._get_records = get_records
        self._upload_file_bytes = upload_file_bytes

    def add_records_with_attachment(
        self,
        docid: str,
        sheet_id: str,
        field_key: str,
        attachments: list[CellAttachmentValue | dict[str, Any]],
        *,
        key_type: CellValueKeyType = CellValueKeyType.CELL_VALUE_KEY_TYPE_FIELD_ID,
    ) -> AddRecordsResponse:
        """新增包含附件字段的记录。"""

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
        return self._add_records(request_payload)

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

        response = self._get_records(request_payload)
        if not response.records:
            raise ValueError(f"未找到记录：{record_id}")

        record = response.records[0]
        if record.record_id != record_id:
            raise ValueError(f"记录ID不匹配：期望 {record_id}，实际 {record.record_id}")

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
        """更新单条记录中的附件字段。"""

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
        return self._update_records(request_payload)

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
    def _guess_file_ext(file_name: str) -> str | None:
        """从文件名推导附件字段所需的扩展名。"""

        if "." not in file_name:
            return None
        suffix = file_name.rsplit(".", 1)[-1].strip()
        return suffix.upper() if suffix else None

    @staticmethod
    def _build_base_attachment(file_name: str, file_bytes: bytes) -> dict[str, Any]:
        """构造写入智能表格附件字段所需的默认元数据。"""

        base_attachment: dict[str, Any] = {
            "name": file_name,
            "size": len(file_bytes),
            "doc_type": 2,
            "file_type": "Wedrive",
        }
        file_ext = SmartSheetAttachmentHelper._guess_file_ext(file_name)
        if file_ext:
            base_attachment["file_ext"] = file_ext
        return base_attachment

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

        upload_req = (
            upload_request
            if isinstance(upload_request, UploadFileRequest)
            else UploadFileRequest.model_validate(upload_request)
        )
        upload_resp = self._client.uploads.upload_file(upload_req)
        file_id = upload_resp.fileid
        if not file_id:
            raise WeComRequestError("上传文件成功但响应缺少 fileid")

        attachment = self._build_attachment_payload(
            file_id,
            attachment_metadata=attachment_metadata,
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
        attachment = self._build_attachment_payload(
            file_id,
            attachment_metadata=attachment_metadata,
            base_attachment=self._build_base_attachment(file_name, file_bytes),
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
        """根据文件字节内容上传到微盘，并更新已有记录的附件字段。"""

        file_id = self._upload_file_bytes(
            file_name=file_name,
            file_bytes=file_bytes,
            spaceid=spaceid,
            fatherid=fatherid,
            selected_ticket=selected_ticket,
        )
        attachment = self._build_attachment_payload(
            file_id,
            attachment_metadata=attachment_metadata,
            base_attachment=self._build_base_attachment(file_name, file_bytes),
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


__all__ = ["SmartSheetAttachmentHelper"]
