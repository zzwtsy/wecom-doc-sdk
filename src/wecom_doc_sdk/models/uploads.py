from __future__ import annotations

from typing import Optional

from pydantic import Field, model_validator

from .common import WeComBaseModel, WeComBaseResponse


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


class UploadFileRequest(WeComBaseModel):
    """上传文件到微盘请求。"""

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
    file_name: str = Field(description="文件名字，最多 255 字符，中文按 2 个字符计数")
    file_base64_content: str = Field(description="文件内容的 Base64 编码字符串")

    @model_validator(mode="after")
    def validate_upload_target(self) -> "UploadFileRequest":
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


class UploadFileResponse(WeComBaseResponse):
    """上传微盘文件响应。"""

    fileid: Optional[str] = Field(default=None, description="上传后返回的文件 fileid")


class ShareFileRequest(WeComBaseModel):
    """获取微盘文件分享链接请求。"""

    fileid: str = Field(description="文件 fileid")


class ShareFileResponse(WeComBaseResponse):
    """获取微盘文件分享链接响应。"""

    share_url: Optional[str] = Field(default=None, description="文件分享链接")
