from __future__ import annotations

from typing import Annotated, Literal

from pydantic import BaseModel, ConfigDict, Field, field_validator, model_validator

from ..models.fields import AddField
from ..models.uploads import CreateSpaceAuthInfo

TEMPLATE_MODE_CREATE = "create"
TEMPLATE_MODE_USE_EXISTING = "use_existing"
TEMPLATE_KIND_SCAFFOLD = "scaffold"
TEMPLATE_KIND_SPACE = "space"
TEMPLATE_KIND_FOLDER = "folder"
TEMPLATE_KIND_SMARTSHEET = "smartsheet"
TEMPLATE_KIND_SHEET = "sheet"
TEMPLATE_KIND_SPACE_ADMIN = "space-admin"
TEMPLATE_KIND_DOC_ADMIN = "doc-admin"


class CLITemplateBaseModel(BaseModel):
    """CLI 模板基础模型。"""

    model_config = ConfigDict(extra="forbid", str_strip_whitespace=True)


class ScaffoldWedriveCreateConfig(CLITemplateBaseModel):
    """创建新微盘空间模式。"""

    mode: Literal["create"] = Field(description="微盘资源模式")
    space_name: str = Field(description="新建空间名称")
    space_sub_type: int | None = Field(default=None, description="空间类型")
    auth_info: list[CreateSpaceAuthInfo] | None = Field(
        default=None, description="空间成员信息"
    )
    folder_name: str | None = Field(default=None, description="新建的单层目录名称")


class ScaffoldWedriveExistingConfig(CLITemplateBaseModel):
    """复用已有微盘空间模式。"""

    mode: Literal["use_existing"] = Field(description="微盘资源模式")
    spaceid: str = Field(description="已有空间 ID")
    fatherid: str = Field(description="已有父目录 ID")


class ScaffoldDocConfig(CLITemplateBaseModel):
    """待创建智能表格文档配置。"""

    title: str = Field(description="智能表格标题")


class ScaffoldSheetConfig(CLITemplateBaseModel):
    """待创建的子表配置。"""

    title: str = Field(description="子表标题")
    fields: list[AddField] = Field(min_length=1, description="字段定义")


WedriveConfig = Annotated[
    ScaffoldWedriveCreateConfig | ScaffoldWedriveExistingConfig,
    Field(discriminator="mode"),
]


class ScaffoldTemplate(CLITemplateBaseModel):
    """脚手架模板定义。"""

    wedrive: WedriveConfig = Field(description="微盘资源配置")
    doc: ScaffoldDocConfig = Field(description="智能表格配置")
    sheets: list[ScaffoldSheetConfig] = Field(min_length=1, description="子表列表")


class SpaceFolderConfig(CLITemplateBaseModel):
    """创建空间时可选的目录配置。"""

    name: str = Field(description="目录名称")


class SpaceTemplate(CLITemplateBaseModel):
    """独立创建微盘空间模板。"""

    space_name: str = Field(description="空间名称")
    space_sub_type: int | None = Field(default=None, description="空间类型")
    auth_info: list[CreateSpaceAuthInfo] | None = Field(
        default=None, description="空间成员信息"
    )
    folder: SpaceFolderConfig | None = Field(default=None, description="可选目录配置")


class FolderTemplate(CLITemplateBaseModel):
    """在已有空间或目录下创建新目录模板。"""

    spaceid: str = Field(description="空间 ID")
    fatherid: str = Field(description="父目录 ID")
    name: str = Field(description="目录名称")


class SheetCreateConfig(CLITemplateBaseModel):
    """子表创建配置。"""

    title: str = Field(description="子表标题")
    index: int | None = Field(default=None, description="子表插入位置")
    fields: list[AddField] | None = Field(default=None, description="可选字段列表")


class SmartSheetTemplate(CLITemplateBaseModel):
    """独立创建智能表格模板。"""

    title: str = Field(description="智能表格标题")
    spaceid: str | None = Field(default=None, description="空间 ID")
    fatherid: str | None = Field(default=None, description="父目录 ID")
    admin_users: list[str] | None = Field(
        default=None, description="文档管理员用户 ID 列表"
    )
    sheet: SheetCreateConfig | None = Field(default=None, description="可选子表配置")


class SheetTemplate(CLITemplateBaseModel):
    """在已有智能表格中创建子表模板。"""

    docid: str = Field(description="智能表格 docid")
    title: str = Field(description="子表标题")
    index: int | None = Field(default=None, description="子表插入位置")
    fields: list[AddField] | None = Field(default=None, description="可选字段列表")


def _normalize_admin_users(admin_users: list[str]) -> list[str]:
    """标准化管理员列表：去空白、去重、保持原顺序。"""

    normalized_users: list[str] = []
    seen: set[str] = set()
    for raw_userid in admin_users:
        userid = raw_userid.strip()
        if not userid:
            raise ValueError("admin_users 不能包含空字符串")
        if userid in seen:
            continue
        seen.add(userid)
        normalized_users.append(userid)
    if not normalized_users:
        raise ValueError("admin_users 至少包含一个 userid")
    return normalized_users


class SpaceAdminAddTemplate(CLITemplateBaseModel):
    """给已有空间添加管理员模板。"""

    spaceid: str = Field(description="已有空间 ID")
    admin_users: list[str] = Field(min_length=1, description="待新增管理员 userid 列表")

    @field_validator("admin_users")
    @classmethod
    def validate_admin_users(cls, value: list[str]) -> list[str]:
        """校验并标准化管理员列表。"""

        return _normalize_admin_users(value)


class DocAdminAddTemplate(CLITemplateBaseModel):
    """给已有文档添加管理员模板。"""

    docid: str = Field(description="已有文档 docid")
    admin_users: list[str] = Field(min_length=1, description="待新增管理员 userid 列表")

    @field_validator("admin_users")
    @classmethod
    def validate_admin_users(cls, value: list[str]) -> list[str]:
        """校验并标准化管理员列表。"""

        return _normalize_admin_users(value)

    @model_validator(mode="after")
    def validate_admin_user_limit(self) -> "DocAdminAddTemplate":
        """文档成员更新接口单批次最多支持 100 人。"""

        if len(self.admin_users) > 100:
            raise ValueError("admin_users 去重后最多支持 100 个 userid")
        return self
