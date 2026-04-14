from __future__ import annotations

from typing import Any, Type, TypeVar

from pydantic import BaseModel

from ..client import WeComClient
from ..models.uploads import (
    AddSpaceAclRequest,
    AddSpaceAclResponse,
    CreateFileRequest,
    CreateFileResponse,
    CreateSpaceRequest,
    CreateSpaceResponse,
    DeleteSpaceAclRequest,
    DeleteSpaceAclResponse,
    FinishFileUploadRequest,
    FinishFileUploadResponse,
    GetSpaceInfoRequest,
    GetSpaceInfoResponse,
    InitFileUploadRequest,
    InitFileUploadResponse,
    ShareFileRequest,
    ShareFileResponse,
    UploadFilePartRequest,
    UploadFilePartResponse,
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

    def create_space(
        self, request: CreateSpaceRequest | dict[str, Any]
    ) -> CreateSpaceResponse:
        """在微盘内新建共享空间。"""
        req = self._ensure_model(CreateSpaceRequest, request)
        data = self._client.request_json(
            "POST",
            "/cgi-bin/wedrive/space_create",
            json=self._client.dump_model(req),
        )
        return CreateSpaceResponse.model_validate(data)

    def add_space_acl(
        self, request: AddSpaceAclRequest | dict[str, Any]
    ) -> AddSpaceAclResponse:
        """向空间添加成员或部门。"""
        req = self._ensure_model(AddSpaceAclRequest, request)
        data = self._client.request_json(
            "POST",
            "/cgi-bin/wedrive/space_acl_add",
            json=self._client.dump_model(req),
        )
        return AddSpaceAclResponse.model_validate(data)

    def delete_space_acl(
        self, request: DeleteSpaceAclRequest | dict[str, Any]
    ) -> DeleteSpaceAclResponse:
        """从空间移除成员或部门。"""
        req = self._ensure_model(DeleteSpaceAclRequest, request)
        data = self._client.request_json(
            "POST",
            "/cgi-bin/wedrive/space_acl_del",
            json=self._client.dump_model(req),
        )
        return DeleteSpaceAclResponse.model_validate(data)

    def get_space_info(
        self, request: GetSpaceInfoRequest | dict[str, Any]
    ) -> GetSpaceInfoResponse:
        """获取空间详情与成员信息。"""
        req = self._ensure_model(GetSpaceInfoRequest, request)
        data = self._client.request_json(
            "POST",
            "/cgi-bin/wedrive/space_info",
            json=self._client.dump_model(req),
        )
        return GetSpaceInfoResponse.model_validate(data)

    def create_file(
        self, request: CreateFileRequest | dict[str, Any]
    ) -> CreateFileResponse:
        """在微盘指定位置创建文件夹或文档。"""
        req = self._ensure_model(CreateFileRequest, request)
        data = self._client.request_json(
            "POST",
            "/cgi-bin/wedrive/file_create",
            json=self._client.dump_model(req),
        )
        return CreateFileResponse.model_validate(data)

    def init_file_upload(
        self, request: InitFileUploadRequest | dict[str, Any]
    ) -> InitFileUploadResponse:
        """初始化微盘文件分块上传。"""
        req = self._ensure_model(InitFileUploadRequest, request)
        data = self._client.request_json(
            "POST",
            "/cgi-bin/wedrive/file_upload_init",
            json=self._client.dump_model(req),
        )
        return InitFileUploadResponse.model_validate(data)

    def upload_file_part(
        self, request: UploadFilePartRequest | dict[str, Any]
    ) -> UploadFilePartResponse:
        """上传微盘文件的单个分块。"""
        req = self._ensure_model(UploadFilePartRequest, request)
        data = self._client.request_json(
            "POST",
            "/cgi-bin/wedrive/file_upload_part",
            json=self._client.dump_model(req),
        )
        return UploadFilePartResponse.model_validate(data)

    def finish_file_upload(
        self, request: FinishFileUploadRequest | dict[str, Any]
    ) -> FinishFileUploadResponse:
        """标记微盘分块上传完成。"""
        req = self._ensure_model(FinishFileUploadRequest, request)
        data = self._client.request_json(
            "POST",
            "/cgi-bin/wedrive/file_upload_finish",
            json=self._client.dump_model(req),
        )
        return FinishFileUploadResponse.model_validate(data)

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
