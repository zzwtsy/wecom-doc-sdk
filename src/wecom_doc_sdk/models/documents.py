from __future__ import annotations

from typing import List, Optional

from pydantic import Field, model_validator

from .common import WeComBaseModel, WeComBaseResponse
from .enums import DocType


class CreateDocRequest(WeComBaseModel):
    """新建文档请求体。"""

    spaceid: Optional[str] = Field(default=None, description="空间 ID，可选")
    fatherid: Optional[str] = Field(default=None, description="父目录 ID，可选")
    # 文档类型：3 文档，4 表格，10 智能表格。
    doc_type: DocType = Field(description="文档类型")
    doc_name: str = Field(description="文档名称")
    admin_users: Optional[List[str]] = Field(
        default=None, description="文档管理员用户 ID 列表"
    )


class CreateDocResponse(WeComBaseResponse):
    """新建文档响应体。"""

    url: Optional[str] = Field(default=None, description="新建文档访问链接")
    docid: Optional[str] = Field(default=None, description="新建文档 ID")


class DocShareRequest(WeComBaseModel):
    """获取文档分享链接请求体。"""

    docid: Optional[str] = Field(default=None, description="文档 ID，与 formid 二选一")
    formid: Optional[str] = Field(
        default=None, description="收集表 ID，与 docid 二选一"
    )

    @model_validator(mode="after")
    def validate_docid_or_formid(self) -> "DocShareRequest":
        """`docid/formid` 必须且只能传一个。"""

        if (self.docid is None) == (self.formid is None):
            raise ValueError("docid 与 formid 必须且只能传入一个")
        return self


class DocShareResponse(WeComBaseResponse):
    """获取文档分享链接响应体。"""

    share_url: Optional[str] = Field(default=None, description="分享链接")


class GetDocBaseInfoRequest(WeComBaseModel):
    """获取文档基础信息请求体。"""

    docid: str = Field(description="文档 ID")


class DocBaseInfo(WeComBaseModel):
    """文档基础信息。"""

    docid: str = Field(description="文档 ID")
    doc_name: str = Field(description="文档名称")
    create_time: int = Field(description="创建时间（秒级时间戳）")
    modify_time: int = Field(description="最后修改时间（秒级时间戳）")
    doc_type: DocType = Field(description="文档类型")


class GetDocBaseInfoResponse(WeComBaseResponse):
    """获取文档基础信息响应体。"""

    doc_base_info: Optional[DocBaseInfo] = Field(
        default=None, description="文档基础信息"
    )


class DeleteDocRequest(WeComBaseModel):
    """删除文档请求体。"""

    docid: Optional[str] = Field(default=None, description="文档 ID，与 formid 二选一")
    formid: Optional[str] = Field(
        default=None, description="收集表 ID，与 docid 二选一"
    )

    @model_validator(mode="after")
    def validate_docid_or_formid(self) -> "DeleteDocRequest":
        """`docid/formid` 必须且只能传一个。"""

        if (self.docid is None) == (self.formid is None):
            raise ValueError("docid 与 formid 必须且只能传入一个")
        return self


class DeleteDocResponse(WeComBaseResponse):
    """删除文档响应体。"""

    pass


class RenameDocRequest(WeComBaseModel):
    """重命名文档请求体。"""

    docid: Optional[str] = Field(default=None, description="文档 ID，与 formid 二选一")
    formid: Optional[str] = Field(
        default=None, description="收集表 ID，与 docid 二选一"
    )
    new_name: str = Field(description="重命名后的名称")

    @model_validator(mode="after")
    def validate_docid_or_formid(self) -> "RenameDocRequest":
        """`docid/formid` 必须且只能传一个。"""

        if (self.docid is None) == (self.formid is None):
            raise ValueError("docid 与 formid 必须且只能传入一个")
        return self


class RenameDocResponse(WeComBaseResponse):
    """重命名文档响应体。"""

    pass
