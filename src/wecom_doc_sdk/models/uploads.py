from __future__ import annotations

from typing import Optional

from pydantic import Field, model_validator

from .common import WeComBaseModel, WeComBaseResponse
from .enums import WedriveFileType


class UploadImageRequest(WeComBaseModel):
    """上传文档图片请求。"""

    docid: str = Field(description="文档 ID")
    base64_content: str = Field(description="base64 编码后的图片内容")


class UploadImageResponse(WeComBaseResponse):
    """上传文档图片响应。"""

    url: Optional[str] = Field(default=None, description="图片访问 URL")
    height: Optional[int] = Field(default=None, description="图片高度")
    width: Optional[int] = Field(default=None, description="图片宽度")
    size: Optional[int] = Field(default=None, description="图片大小，字节")


class WedriveUploadTargetRequest(WeComBaseModel):
    """微盘上传目标请求基类。"""

    spaceid: Optional[str] = Field(default=None, description="微盘空间 ID")
    fatherid: Optional[str] = Field(
        default=None, description="父目录 fileid，根目录时可使用 spaceid"
    )
    selected_ticket: Optional[str] = Field(
        default=None,
        description=(
            "微盘和文件选择器 JSAPI 返回的 selected_ticket，"
            "填入后无需同时填写 spaceid/fatherid"
        ),
    )

    @model_validator(mode="after")
    def validate_upload_target(self) -> "WedriveUploadTargetRequest":
        """校验上传目标参数。

        规则：
        1. `selected_ticket` 与 `spaceid/fatherid` 必须二选一；
        2. 使用 `spaceid/fatherid` 组时，二者必须同时填写。
        """

        has_selected_ticket = bool(self.selected_ticket)
        has_spaceid = bool(self.spaceid)
        has_fatherid = bool(self.fatherid)

        if has_selected_ticket and (has_spaceid or has_fatherid):
            raise ValueError(
                "selected_ticket 与 spaceid/fatherid 不能同时填写，必须仅选择一组参数"
            )

        if has_selected_ticket:
            return self

        if has_spaceid and has_fatherid:
            return self

        raise ValueError(
            "必须填写 selected_ticket，或同时填写 spaceid 与 fatherid"
        )


class UploadFileRequest(WedriveUploadTargetRequest):
    """上传文件到微盘请求。"""

    file_name: str = Field(description="文件名字，最多 255 字符，中文按 2 个字符计数")
    file_base64_content: str = Field(description="文件内容的 Base64 编码字符串")


class UploadFileResponse(WeComBaseResponse):
    """上传微盘文件响应。"""

    fileid: Optional[str] = Field(default=None, description="上传后返回的文件 fileid")


class ShareFileRequest(WeComBaseModel):
    """获取微盘文件分享链接请求。"""

    fileid: str = Field(description="文件 fileid")


class ShareFileResponse(WeComBaseResponse):
    """获取微盘文件分享链接响应。"""

    share_url: Optional[str] = Field(default=None, description="文件分享链接")


class CreateSpaceAuthInfo(WeComBaseModel):
    """微盘空间成员授权信息。"""

    type: int = Field(description="成员类型，1 为成员，2 为部门")
    userid: Optional[str] = Field(default=None, description="成员 userid")
    departmentid: Optional[int] = Field(default=None, description="部门 ID")
    auth: int = Field(
        description="成员权限，1 为仅下载，4 为可预览，7 为应用空间管理员"
    )

    @model_validator(mode="after")
    def validate_member_scope(self) -> "CreateSpaceAuthInfo":
        """校验空间成员范围与权限组合。"""

        if self.type == 1:
            if not self.userid:
                raise ValueError("type=1 时必须填写 userid")
            if self.departmentid is not None:
                raise ValueError("type=1 时不能填写 departmentid")
            return self

        if self.type == 2:
            if self.departmentid is None:
                raise ValueError("type=2 时必须填写 departmentid")
            if self.userid:
                raise ValueError("type=2 时不能填写 userid")
            if self.auth == 7:
                raise ValueError("部门类型不支持设置 auth=7 的应用空间管理员权限")
            return self

        raise ValueError("type 仅支持 1（成员）或 2（部门）")


class CreateSpaceRequest(WeComBaseModel):
    """新建微盘空间请求。"""

    space_name: str = Field(description="空间标题")
    auth_info: Optional[list[CreateSpaceAuthInfo]] = Field(
        default=None, description="空间成员信息"
    )
    space_sub_type: Optional[int] = Field(
        default=None, description="空间类型，当前仅支持 0"
    )


class CreateSpaceResponse(WeComBaseResponse):
    """新建微盘空间响应。"""

    spaceid: Optional[str] = Field(default=None, description="空间 ID")


class AddSpaceAclRequest(WeComBaseModel):
    """向空间添加成员或部门请求。"""

    spaceid: str = Field(description="空间 ID")
    auth_info: list[CreateSpaceAuthInfo] = Field(description="待添加的空间成员信息")


class AddSpaceAclResponse(WeComBaseResponse):
    """向空间添加成员或部门响应。"""


class DeleteSpaceAclAuthInfo(WeComBaseModel):
    """空间成员移除信息。"""

    type: int = Field(description="成员类型，1 为成员，2 为部门")
    userid: Optional[str] = Field(default=None, description="成员 userid")
    departmentid: Optional[int] = Field(default=None, description="部门 ID")

    @model_validator(mode="after")
    def validate_member_scope(self) -> "DeleteSpaceAclAuthInfo":
        """校验被移除的成员范围。"""

        if self.type == 1:
            if not self.userid:
                raise ValueError("type=1 时必须填写 userid")
            if self.departmentid is not None:
                raise ValueError("type=1 时不能填写 departmentid")
            return self

        if self.type == 2:
            if self.departmentid is None:
                raise ValueError("type=2 时必须填写 departmentid")
            if self.userid:
                raise ValueError("type=2 时不能填写 userid")
            return self

        raise ValueError("type 仅支持 1（成员）或 2（部门）")


class DeleteSpaceAclRequest(WeComBaseModel):
    """从空间移除成员或部门请求。"""

    spaceid: str = Field(description="空间 ID")
    auth_info: list[DeleteSpaceAclAuthInfo] = Field(description="待移除的空间成员信息")


class DeleteSpaceAclResponse(WeComBaseResponse):
    """从空间移除成员或部门响应。"""


class GetSpaceInfoRequest(WeComBaseModel):
    """获取空间信息请求。"""

    spaceid: str = Field(description="空间 ID")


class SpaceAuthList(WeComBaseModel):
    """空间成员列表。"""

    auth_info: Optional[list[CreateSpaceAuthInfo]] = Field(
        default=None, description="空间成员信息"
    )
    quit_userid: Optional[list[str]] = Field(
        default=None, description="无权限但仍在授权部门中的成员 userid 列表"
    )


class SpaceInfo(WeComBaseModel):
    """空间详情。"""

    spaceid: Optional[str] = Field(default=None, description="空间 ID")
    space_name: Optional[str] = Field(default=None, description="空间名称")
    auth_list: Optional[SpaceAuthList] = Field(default=None, description="空间成员列表")
    space_sub_type: Optional[int] = Field(default=None, description="空间类型")


class GetSpaceInfoResponse(WeComBaseResponse):
    """获取空间信息响应。"""

    space_info: Optional[SpaceInfo] = Field(default=None, description="空间详情")


class CreateFileRequest(WeComBaseModel):
    """在微盘指定位置新建文件夹或文档请求。"""

    spaceid: str = Field(description="空间 ID")
    fatherid: str = Field(description="父目录 fileid，根目录时传 spaceid")
    file_type: WedriveFileType = Field(description="文件类型")
    file_name: str = Field(description="文件名")


class CreateFileResponse(WeComBaseResponse):
    """微盘创建文件响应。"""

    fileid: Optional[str] = Field(default=None, description="新建文件的 fileid")
    url: Optional[str] = Field(default=None, description="新建文档时返回的访问链接")


class InitFileUploadRequest(WedriveUploadTargetRequest):
    """分块上传初始化请求。"""

    file_name: str = Field(description="文件名")
    size: int = Field(description="文件大小，单位字节，最大支持 20G")
    block_sha: list[str] = Field(description="按分块顺序排列的累积 sha1 值")
    skip_push_card: Optional[bool] = Field(
        default=None, description="文件创建完成时是否跳过推送企业微信卡片"
    )


class InitFileUploadResponse(WeComBaseResponse):
    """分块上传初始化响应。"""

    hit_exist: Optional[bool] = Field(default=None, description="是否命中秒传")
    upload_key: Optional[str] = Field(default=None, description="上传凭证")
    fileid: Optional[str] = Field(default=None, description="命中秒传时返回的文件 ID")


class UploadFilePartRequest(WeComBaseModel):
    """上传单个文件分块请求。"""

    upload_key: str = Field(description="上传凭证")
    index: int = Field(description="分块索引，从 1 开始")
    file_base64_content: str = Field(description="当前分块的 Base64 内容")


class UploadFilePartResponse(WeComBaseResponse):
    """上传单个文件分块响应。"""


class FinishFileUploadRequest(WeComBaseModel):
    """分块上传完成请求。"""

    upload_key: str = Field(description="上传凭证")


class FinishFileUploadResponse(WeComBaseResponse):
    """分块上传完成响应。"""

    fileid: Optional[str] = Field(default=None, description="上传完成后的文件 ID")
