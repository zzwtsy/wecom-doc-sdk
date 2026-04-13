from __future__ import annotations

from typing import Any, Type, TypeVar

from pydantic import BaseModel

from ..client import WeComClient
from ..models.uploads import (
    ShareFileRequest,
    ShareFileResponse,
    UploadFileRequest,
    UploadFileResponse,
    UploadImageRequest,
    UploadImageResponse,
)

TModel = TypeVar("TModel", bound=BaseModel)


class UploadsAPI:
    """素材上传相关接口封装。"""

    def __init__(self, client: WeComClient) -> None:
        self._client = client

    @staticmethod
    def _ensure_model(model_cls: Type[TModel], payload: Any) -> TModel:
        if isinstance(payload, model_cls):
            return payload
        return model_cls.model_validate(payload)

    def upload_image(
        self, request: UploadImageRequest | dict[str, Any]
    ) -> UploadImageResponse:
        """上传图片到文档素材管理。"""
        req = self._ensure_model(UploadImageRequest, request)
        data = self._client.request_json(
            "POST",
            "/cgi-bin/wedoc/image_upload",
            json=self._client.dump_model(req),
        )
        return UploadImageResponse.model_validate(data)

    def upload_file(
        self, request: UploadFileRequest | dict[str, Any]
    ) -> UploadFileResponse:
        """上传文件到微盘。"""
        req = self._ensure_model(UploadFileRequest, request)
        data = self._client.request_json(
            "POST",
            "/cgi-bin/wedrive/file_upload",
            json=self._client.dump_model(req),
        )
        return UploadFileResponse.model_validate(data)

    def share_file(
        self, request: ShareFileRequest | dict[str, Any]
    ) -> ShareFileResponse:
        """获取微盘文件分享链接。"""
        req = self._ensure_model(ShareFileRequest, request)
        data = self._client.request_json(
            "POST",
            "/cgi-bin/wedrive/file_share",
            json=self._client.dump_model(req),
        )
        return ShareFileResponse.model_validate(data)
