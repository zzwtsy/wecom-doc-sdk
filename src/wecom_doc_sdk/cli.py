from __future__ import annotations

import argparse
import importlib
import json
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Annotated, Any, Literal

from pydantic import BaseModel, ConfigDict, Field, ValidationError

from .client import WeComClient
from .models.documents import CreateDocRequest
from .models.enums import DocType, WedriveFileType
from .models.fields import AddField, AddFieldsRequest
from .models.sheets import AddSheetProperties, AddSheetRequest
from .models.uploads import CreateFileRequest, CreateSpaceAuthInfo, CreateSpaceRequest

TEMPLATE_MODE_CREATE = "create"
TEMPLATE_MODE_USE_EXISTING = "use_existing"


class CLIError(Exception):
    """CLI 执行失败时抛出的可读错误。"""


class CLITemplateBaseModel(BaseModel):
    """CLI 模板基础模型。

    模板是面向用户维护的配置文件，这里改成严格模式，尽量尽早暴露拼写问题和多余字段。
    """

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


def _load_yaml_module() -> Any:
    """延迟加载 PyYAML，避免在未安装依赖时导入整个包即失败。"""

    try:
        return importlib.import_module("yaml")
    except ModuleNotFoundError as exc:
        raise CLIError(
            "未安装 PyYAML，无法读取 YAML 模板。"
            "请先执行 `uv sync --dev` 或安装 PyYAML。"
        ) from exc


def load_scaffold_template(template_path: Path) -> ScaffoldTemplate:
    """读取并校验脚手架模板。"""

    if not template_path.exists():
        raise CLIError(f"模板文件不存在：{template_path}")
    if not template_path.is_file():
        raise CLIError(f"模板路径不是文件：{template_path}")

    yaml = _load_yaml_module()
    try:
        payload = yaml.safe_load(template_path.read_text(encoding="utf-8"))
    except Exception as exc:  # pragma: no cover - 依赖 PyYAML 的具体异常类型
        raise CLIError(f"读取 YAML 模板失败：{exc}") from exc

    if payload is None:
        raise CLIError("模板文件内容为空")
    if not isinstance(payload, dict):
        raise CLIError("模板顶层必须是对象")

    try:
        return ScaffoldTemplate.model_validate(payload)
    except ValidationError as exc:
        raise CLIError(f"模板校验失败：{exc}") from exc


def resolve_non_conflicting_path(base_path: Path) -> Path:
    """计算不与已有文件冲突的输出路径。

    如果目标文件已存在，会自动追加数字后缀，避免直接覆盖已有结果。
    """

    if not base_path.exists():
        return base_path

    suffix = "".join(base_path.suffixes)
    stem = base_path.name[: -len(suffix)] if suffix else base_path.name
    index = 1
    while True:
        candidate_name = f"{stem}.{index}{suffix}"
        candidate = base_path.with_name(candidate_name)
        if not candidate.exists():
            return candidate
        index += 1


def resolve_manifest_path(template_path: Path, output_path: Path | None) -> Path:
    """计算 manifest 输出路径。"""

    base_path = output_path or template_path.with_name(
        f"{template_path.stem}.manifest.json"
    )
    return resolve_non_conflicting_path(base_path)


def build_template_content(mode: Literal["create", "use_existing"]) -> str:
    """生成带中文注释的 YAML 模板内容。"""

    doc_section = """# 智能表格文档配置。
doc:
  # 智能表格标题。
  title: 示例智能表

# 子表定义。
# 下面先给一张常用的附件表示例；你可以继续在 sheets 下追加更多子表。
sheets:
  - # 子表标题。
    title: 附件表
    # 字段定义列表；列表中的每一项都会创建成一个字段，顺序与这里保持一致。
    # `field_title` 是字段显示名称，`field_type` 是字段类型枚举值。
    # 如果需要更复杂的字段能力，可以继续补充对应的 `property_*` 配置。
    fields:
      - # 文本字段示例，通常用来记录原始文件名或业务标题。
        field_title: 文件名
        field_type: FIELD_TYPE_TEXT
      - # 附件字段示例，用来写入微盘文件元数据。
        field_title: 附件
        field_type: FIELD_TYPE_ATTACHMENT
"""

    if mode == TEMPLATE_MODE_CREATE:
        wedrive_section = """# 微盘资源配置。
# `create` 模式会先创建空间，再可选创建一个单层目录。
wedrive:
  # `create` 表示本次脚手架会主动创建新的微盘空间。
  mode: create
  # 新空间名称，请改成你的业务名称。
  space_name: 示例空间
  # 空间类型，当前保持 0 即可。
  space_sub_type: 0
  # 可选目录名称；填写后会在空间根目录下创建一个文件夹。
  folder_name: 附件目录
  # 如需给空间附加成员或管理员，可参考下面的注释示例。
  # auth_info:
  #   # `type` 表示授权对象类型：1=成员，2=部门。
  #   - type: 1
  #     # 当 type=1 时填写 userid；当 type=2 时改填 departmentid。
  #     userid: zhangsan
  #     # `auth` 表示权限：1=仅下载，4=可预览，7=应用空间管理员。
  #     auth: 7
"""
    else:
        wedrive_section = """# 微盘资源配置。
# `use_existing` 模式会直接复用现成空间和目录。
wedrive:
  # `use_existing` 表示脚手架不会创建新空间。
  mode: use_existing
  # 已有微盘空间 ID。
  spaceid: SPACEID
  # 已有父目录 ID；如果要直接使用空间根目录，可填 spaceid。
  fatherid: FOLDERID
"""

    return (
        "# 企业微信智能表格脚手架模板。\n"
        "# 这份模板可以直接交给 `wecom-doc-sdk scaffold` 使用。\n"
        "# 请按你的业务场景修改示例值。\n\n"
        f"{wedrive_section}\n"
        f"{doc_section}"
    )


def run_init_template(
    *,
    template_path: Path,
    mode: Literal["create", "use_existing"] = TEMPLATE_MODE_CREATE,
) -> Path:
    """生成带注释的 YAML 模板文件。"""

    final_path = resolve_non_conflicting_path(template_path)
    final_path.parent.mkdir(parents=True, exist_ok=True)
    final_path.write_text(build_template_content(mode), encoding="utf-8")
    print(f"已生成模板：{final_path}")
    return final_path


def build_dry_run_summary(
    template: ScaffoldTemplate, template_path: Path, manifest_path: Path
) -> dict[str, Any]:
    """生成 dry-run 输出。"""

    actions: list[dict[str, Any]] = []
    if isinstance(template.wedrive, ScaffoldWedriveCreateConfig):
        actions.append(
            {
                "step": "create_space",
                "space_name": template.wedrive.space_name,
                "space_sub_type": template.wedrive.space_sub_type,
                "auth_info_count": len(template.wedrive.auth_info or []),
            }
        )
        if template.wedrive.folder_name:
            actions.append(
                {
                    "step": "create_folder",
                    "folder_name": template.wedrive.folder_name,
                }
            )
    else:
        actions.append(
            {
                "step": "use_existing_wedrive",
                "spaceid": template.wedrive.spaceid,
                "fatherid": template.wedrive.fatherid,
            }
        )

    actions.append(
        {
            "step": "create_doc",
            "title": template.doc.title,
            "doc_type": DocType.SMARTSHEET.value,
        }
    )
    for index, sheet in enumerate(template.sheets):
        actions.append(
            {
                "step": "add_sheet",
                "index": index,
                "title": sheet.title,
            }
        )
        actions.append(
            {
                "step": "add_fields",
                "sheet_title": sheet.title,
                "field_titles": [field.field_title for field in sheet.fields],
            }
        )

    return {
        "mode": "dry-run",
        "template_path": str(template_path.resolve()),
        "manifest_path": str(manifest_path.resolve()),
        "actions": actions,
    }


def _require_value(value: str | None, field_name: str, action_name: str) -> str:
    """校验关键响应字段不能为空。"""

    if not value:
        raise CLIError(f"{action_name} 返回缺少 {field_name}")
    return value


def run_scaffold(
    *,
    corp_id: str,
    corp_secret: str,
    template_path: Path,
    output_path: Path | None = None,
    dry_run: bool = False,
) -> Path:
    """执行脚手架命令并返回 manifest 路径。"""

    template = load_scaffold_template(template_path)
    manifest_path = resolve_manifest_path(template_path, output_path)

    if dry_run:
        print(
            json.dumps(
                build_dry_run_summary(template, template_path, manifest_path),
                ensure_ascii=False,
                indent=2,
            )
        )
        return manifest_path

    with WeComClient(corp_id, corp_secret) as client:
        if isinstance(template.wedrive, ScaffoldWedriveCreateConfig):
            create_space_response = client.uploads.create_space(
                CreateSpaceRequest(
                    space_name=template.wedrive.space_name,
                    space_sub_type=template.wedrive.space_sub_type,
                    auth_info=template.wedrive.auth_info,
                )
            )
            spaceid = _require_value(
                create_space_response.spaceid, "spaceid", "create_space"
            )
            fatherid = spaceid
            if template.wedrive.folder_name:
                create_folder_response = client.uploads.create_file(
                    CreateFileRequest(
                        spaceid=spaceid,
                        fatherid=spaceid,
                        file_type=WedriveFileType.FOLDER,
                        file_name=template.wedrive.folder_name,
                    )
                )
                fatherid = _require_value(
                    create_folder_response.fileid, "fileid", "create_file"
                )
        else:
            spaceid = template.wedrive.spaceid
            fatherid = template.wedrive.fatherid

        create_doc_response = client.documents.create_doc(
            CreateDocRequest(
                spaceid=spaceid,
                fatherid=fatherid,
                doc_type=DocType.SMARTSHEET,
                doc_name=template.doc.title,
            )
        )
        docid = _require_value(create_doc_response.docid, "docid", "create_doc")

        manifest_sheets: list[dict[str, Any]] = []
        for index, sheet in enumerate(template.sheets):
            add_sheet_response = client.smartsheet.add_sheet(
                AddSheetRequest(
                    docid=docid,
                    properties=AddSheetProperties(title=sheet.title, index=index),
                )
            )
            sheet_id = _require_value(
                add_sheet_response.properties.sheet_id
                if add_sheet_response.properties
                else None,
                "sheet_id",
                "add_sheet",
            )
            add_fields_response = client.smartsheet.add_fields(
                AddFieldsRequest(docid=docid, sheet_id=sheet_id, fields=sheet.fields)
            )
            if not add_fields_response.fields:
                raise CLIError("add_fields 返回缺少 fields")

            manifest_fields: dict[str, dict[str, Any]] = {}
            for field in add_fields_response.fields:
                field_title = _require_value(
                    field.field_title, "field_title", "add_fields"
                )
                field_id = _require_value(field.field_id, "field_id", "add_fields")
                manifest_fields[field_title] = {
                    "field_id": field_id,
                    "field_type": field.field_type.value if field.field_type else None,
                }

            manifest_sheets.append(
                {
                    "title": sheet.title,
                    "sheet_id": sheet_id,
                    "fields": manifest_fields,
                }
            )

    manifest = {
        "template_path": str(template_path.resolve()),
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "wedrive": {
            "spaceid": spaceid,
            "fatherid": fatherid,
        },
        "doc": {
            "docid": docid,
            "title": template.doc.title,
        },
        "sheets": manifest_sheets,
    }

    manifest_path.parent.mkdir(parents=True, exist_ok=True)
    manifest_path.write_text(
        json.dumps(manifest, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )
    print(f"已生成 manifest：{manifest_path}")
    return manifest_path


def build_parser() -> argparse.ArgumentParser:
    """构建命令行参数解析器。"""

    parser = argparse.ArgumentParser(prog="wecom-doc-sdk")
    subparsers = parser.add_subparsers(dest="command")

    scaffold_parser = subparsers.add_parser(
        "scaffold", help="根据 YAML 模板创建微盘空间和智能表格"
    )
    scaffold_parser.add_argument("template_path", help="YAML 模板路径")
    scaffold_parser.add_argument("--corp-id", required=True, help="企业微信 CorpID")
    scaffold_parser.add_argument(
        "--corp-secret", required=True, help="企业微信应用 Secret"
    )
    scaffold_parser.add_argument("--output", help="manifest 输出路径")
    scaffold_parser.add_argument(
        "--dry-run", action="store_true", help="只输出计划，不调用写接口"
    )

    template_parser = subparsers.add_parser(
        "init-template", help="生成可直接用于 scaffold 的 YAML 模板"
    )
    template_parser.add_argument("template_path", help="模板输出路径")
    template_parser.add_argument(
        "--mode",
        choices=[TEMPLATE_MODE_CREATE, TEMPLATE_MODE_USE_EXISTING],
        default=TEMPLATE_MODE_CREATE,
        help="模板模式，默认 create",
    )

    return parser


def main(argv: list[str] | None = None) -> int:
    """CLI 入口。"""

    parser = build_parser()
    args = parser.parse_args(argv)

    if args.command == "init-template":
        try:
            run_init_template(
                template_path=Path(args.template_path),
                mode=args.mode,
            )
        except CLIError as exc:
            print(str(exc), file=sys.stderr)
            return 1
        return 0

    if args.command != "scaffold":
        parser.print_help()
        return 1

    try:
        run_scaffold(
            corp_id=args.corp_id,
            corp_secret=args.corp_secret,
            template_path=Path(args.template_path),
            output_path=Path(args.output) if args.output else None,
            dry_run=bool(args.dry_run),
        )
    except CLIError as exc:
        print(str(exc), file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":  # pragma: no cover - 供手工执行
    raise SystemExit(main())
