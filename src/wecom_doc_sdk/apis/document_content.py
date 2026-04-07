from __future__ import annotations

from typing import Any, Type, TypeVar

from pydantic import BaseModel

from ..client import WeComClient
from ..models.document_content import (
    BatchUpdateDocumentRequest,
    BatchUpdateDocumentResponse,
    GetDocumentRequest,
    GetDocumentResponse,
)

TModel = TypeVar("TModel", bound=BaseModel)


class DocumentContentAPI:
    """管理文档内容相关接口封装。"""

    def __init__(self, client: WeComClient) -> None:
        self._client = client

    @staticmethod
    def _ensure_model(model_cls: Type[TModel], payload: Any) -> TModel:
        if isinstance(payload, model_cls):
            return payload
        return model_cls.model_validate(payload)

    def batch_update(
        self, request: BatchUpdateDocumentRequest | dict[str, Any]
    ) -> BatchUpdateDocumentResponse:
        """批量编辑文档内容。"""
        req = self._ensure_model(BatchUpdateDocumentRequest, request)
        data = self._client.request_json(
            "POST",
            "/cgi-bin/wedoc/document/batch_update",
            json=self._client.dump_model(req),
        )
        return BatchUpdateDocumentResponse.model_validate(data)

    def get(self, request: GetDocumentRequest | dict[str, Any]) -> GetDocumentResponse:
        """获取文档数据。"""
        req = self._ensure_model(GetDocumentRequest, request)
        data = self._client.request_json(
            "POST",
            "/cgi-bin/wedoc/document/get",
            json=self._client.dump_model(req),
        )
        return GetDocumentResponse.model_validate(data)
