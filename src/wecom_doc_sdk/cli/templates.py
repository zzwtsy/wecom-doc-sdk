from __future__ import annotations

from .errors import CLIError
from .models import (
    TEMPLATE_KIND_DOC_ADMIN,
    TEMPLATE_KIND_FOLDER,
    TEMPLATE_KIND_SHEET,
    TEMPLATE_KIND_SMARTSHEET,
    TEMPLATE_KIND_SPACE,
    TEMPLATE_KIND_SPACE_ADMIN,
)


def build_space_template_content() -> str:
    return """# 微盘空间模板。
# 这份模板可直接交给 `wecom-doc-sdk space create` 使用。
# 如果填写 folder，会在创建空间后顺带创建一个单层目录。

# 新空间名称。
space_name: 示例空间
# 空间类型，当前保持 0 即可。
space_sub_type: 0
# 可选的空间成员或管理员配置。
# auth_info:
#   # `type` 表示授权对象类型：1=成员，2=部门。
#   - type: 1
#     # 当 type=1 时填写 userid；当 type=2 时改填 departmentid。
#     userid: zhangsan
#     # `auth` 表示权限：1=仅下载，4=可预览，7=应用空间管理员。
#     auth: 7
# 可选目录配置；填写后会在空间根目录下创建一个文件夹。
# folder:
#   name: 附件目录
"""


def build_folder_template_content() -> str:
    return """# 微盘目录模板。
# 这份模板可直接交给 `wecom-doc-sdk space folder create` 使用。

# 已有微盘空间 ID。
spaceid: SPACEID
# 父目录 ID；如果直接放在空间根目录，可填 spaceid。
fatherid: FOLDERID
# 新目录名称。
name: 附件目录
"""


def build_smartsheet_template_content() -> str:
    return """# 智能表格模板。
# 这份模板可直接交给 `wecom-doc-sdk smartsheet create` 使用。
# 如果填写 sheets，会在创建智能表格后顺带创建多个子表。

# 智能表格标题。
title: 示例智能表
# 可选空间 ID；填写后会把智能表格创建到对应空间或目录下。
# spaceid: SPACEID
# 可选父目录 ID；通常与 spaceid 配合使用。
# fatherid: FOLDERID
# 可选文档管理员列表。
# admin_users:
#   - zhangsan
# 可选子表配置列表。
# sheets:
#   - title: 附件表
#     index: 0
#     fields:
#       - field_title: 文件名
#         field_type: FIELD_TYPE_TEXT
#       - field_title: 附件
#         field_type: FIELD_TYPE_ATTACHMENT
"""


def build_sheet_template_content() -> str:
    return """# 智能表格子表模板。
# 这份模板可直接交给 `wecom-doc-sdk smartsheet sheet create` 使用。
# 如果填写 fields，会在创建子表后继续创建字段。

# 已有智能表格的 docid。
docid: DOCID
# 子表标题。
title: 附件表
# 可选插入位置。
# index: 0
# 可选字段列表。
# fields:
#   - field_title: 文件名
#     field_type: FIELD_TYPE_TEXT
#   - field_title: 附件
#     field_type: FIELD_TYPE_ATTACHMENT
"""


def build_space_admin_template_content() -> str:
    return """# 空间管理员添加模板。
# 这份模板可直接交给 `wecom-doc-sdk space admin add` 使用。

# 已有微盘空间 ID。
spaceid: SPACEID
# 待新增为管理员的成员 userid 列表。
# 列表会在命令执行前自动去空白和去重。
admin_users:
  - zhangsan
  - lisi
"""


def build_doc_admin_template_content() -> str:
    return """# 文档管理员添加模板。
# 这份模板可直接交给 `wecom-doc-sdk doc admin add` 使用。

# 已有文档 docid（支持文档/表格/智能表格）。
docid: DOCID
# 待新增为管理员的成员 userid 列表。
# 列表会在命令执行前自动去空白和去重，且单次最多 100 人。
admin_users:
  - zhangsan
  - lisi
"""


def build_template_content(
    kind: str,
) -> str:
    if kind == TEMPLATE_KIND_SPACE:
        return build_space_template_content()
    if kind == TEMPLATE_KIND_FOLDER:
        return build_folder_template_content()
    if kind == TEMPLATE_KIND_SMARTSHEET:
        return build_smartsheet_template_content()
    if kind == TEMPLATE_KIND_SHEET:
        return build_sheet_template_content()
    if kind == TEMPLATE_KIND_SPACE_ADMIN:
        return build_space_admin_template_content()
    if kind == TEMPLATE_KIND_DOC_ADMIN:
        return build_doc_admin_template_content()
    raise CLIError(f"不支持的模板类型：{kind}")
