from __future__ import annotations

from typing import Any, Type, TypeVar

from pydantic import BaseModel

from ..client import WeComClient
from ..models.documents import (
    CreateDocRequest,
    CreateDocResponse,
    DeleteDocRequest,
    DeleteDocResponse,
    DocShareRequest,
    DocShareResponse,
    GetDocBaseInfoRequest,
    GetDocBaseInfoResponse,
    RenameDocRequest,
    RenameDocResponse,
)

TModel = TypeVar("TModel", bound=BaseModel)


class DocumentsAPI:
    """管理文档相关接口封装。"""

    def __init__(self, client: WeComClient) -> None:
        self._client = client

    @staticmethod
    def _ensure_model(model_cls: Type[TModel], payload: Any) -> TModel:
        if isinstance(payload, model_cls):
            return payload
        return model_cls.model_validate(payload)

    def create_doc(
        self, request: CreateDocRequest | dict[str, Any]
    ) -> CreateDocResponse:
        """新建文档、表格或智能表格。"""
        req = self._ensure_model(CreateDocRequest, request)
        data = self._client.request_json(
            "POST",
            "/cgi-bin/wedoc/create_doc",
            json=self._client.dump_model(req),
        )
        return CreateDocResponse.model_validate(data)

    def doc_share(self, request: DocShareRequest | dict[str, Any]) -> DocShareResponse:
        """获取文档、智能表格或收集表分享链接。"""
        req = self._ensure_model(DocShareRequest, request)
        data = self._client.request_json(
            "POST",
            "/cgi-bin/wedoc/doc_share",
            json=self._client.dump_model(req),
        )
        return DocShareResponse.model_validate(data)

    def get_doc_base_info(
        self, request: GetDocBaseInfoRequest | dict[str, Any]
    ) -> GetDocBaseInfoResponse:
        """获取文档基础信息。"""
        req = self._ensure_model(GetDocBaseInfoRequest, request)
        data = self._client.request_json(
            "POST",
            "/cgi-bin/wedoc/get_doc_base_info",
            json=self._client.dump_model(req),
        )
        return GetDocBaseInfoResponse.model_validate(data)

    def delete_doc(
        self, request: DeleteDocRequest | dict[str, Any]
    ) -> DeleteDocResponse:
        """删除文档或收集表。"""
        req = self._ensure_model(DeleteDocRequest, request)
        data = self._client.request_json(
            "POST",
            "/cgi-bin/wedoc/del_doc",
            json=self._client.dump_model(req),
        )
        return DeleteDocResponse.model_validate(data)

    def rename_doc(
        self, request: RenameDocRequest | dict[str, Any]
    ) -> RenameDocResponse:
        """重命名文档或收集表。"""
        req = self._ensure_model(RenameDocRequest, request)
        data = self._client.request_json(
            "POST",
            "/cgi-bin/wedoc/rename_doc",
            json=self._client.dump_model(req),
        )
        return RenameDocResponse.model_validate(data)
