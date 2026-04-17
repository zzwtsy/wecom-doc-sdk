from __future__ import annotations

import argparse
import sys
from pathlib import Path
from typing import NoReturn

from .commands.doc import run_doc_admin_add
from .commands.scaffold import run_scaffold
from .commands.smartsheet import run_smartsheet_create, run_smartsheet_sheet_create
from .commands.space import (
    run_space_admin_add,
    run_space_create,
    run_space_folder_create,
)
from .commands.template import run_template_init
from .errors import CLIError
from .models import (
    TEMPLATE_KIND_SCAFFOLD,
    TEMPLATE_MODE_CREATE,
    TEMPLATE_MODE_USE_EXISTING,
)
from .utils import add_auth_args


class CLIArgumentParserExit(Exception):
    """参数解析终止。"""

    def __init__(self, status: int) -> None:
        self.status = status
        super().__init__(status)


class CLIArgumentParser(argparse.ArgumentParser):
    """将 argparse 退出改为可返回的状态码。"""

    def exit(self, status: int = 0, message: str | None = None) -> NoReturn:
        if message:
            print(message, file=sys.stderr, end="")
        raise CLIArgumentParserExit(status)


def add_required_subparsers(
    parser: argparse.ArgumentParser, *, dest: str
) -> argparse._SubParsersAction[argparse.ArgumentParser]:
    """创建必须填写的子命令解析器。"""

    return parser.add_subparsers(dest=dest, required=True)


def build_parser() -> argparse.ArgumentParser:
    """构建命令行参数解析器。"""

    parser = CLIArgumentParser(prog="wecom-doc-sdk")
    subparsers = add_required_subparsers(parser, dest="command")

    scaffold_parser = subparsers.add_parser(
        "scaffold", help="根据 YAML 模板创建微盘空间和智能表格"
    )
    scaffold_parser.add_argument("template_path", help="YAML 模板路径")
    add_auth_args(scaffold_parser, required=False)
    scaffold_parser.add_argument("--output", help="manifest 输出路径")
    scaffold_parser.add_argument(
        "--dry-run", action="store_true", help="只输出计划，不调用写接口"
    )

    template_parser = subparsers.add_parser("template", help="模板相关命令")
    template_subparsers = add_required_subparsers(
        template_parser, dest="template_command"
    )
    template_init_parser = template_subparsers.add_parser(
        "init", help="生成带注释的 YAML 模板"
    )
    template_kind_subparsers = add_required_subparsers(
        template_init_parser, dest="template_kind"
    )
    scaffold_template_parser = template_kind_subparsers.add_parser(
        TEMPLATE_KIND_SCAFFOLD, help="生成脚手架 YAML 模板"
    )
    scaffold_template_parser.add_argument("template_path", help="模板输出路径")
    scaffold_template_parser.add_argument(
        "--mode",
        choices=[TEMPLATE_MODE_CREATE, TEMPLATE_MODE_USE_EXISTING],
        default=TEMPLATE_MODE_CREATE,
        help="脚手架模板模式，默认 create",
    )
    for template_kind, help_text in (
        ("space", "生成微盘空间 YAML 模板"),
        ("folder", "生成微盘目录 YAML 模板"),
        ("smartsheet", "生成智能表格 YAML 模板"),
        ("sheet", "生成子表 YAML 模板"),
        ("space-admin", "生成空间管理员 YAML 模板"),
        ("doc-admin", "生成文档管理员 YAML 模板"),
    ):
        template_kind_parser = template_kind_subparsers.add_parser(
            template_kind, help=help_text
        )
        template_kind_parser.add_argument("template_path", help="模板输出路径")

    space_parser = subparsers.add_parser("space", help="微盘空间相关命令")
    space_subparsers = add_required_subparsers(space_parser, dest="space_command")
    space_create_parser = space_subparsers.add_parser(
        "create", help="根据 YAML 模板创建空间"
    )
    space_create_parser.add_argument("template_path", help="空间模板路径")
    add_auth_args(space_create_parser)

    space_folder_parser = space_subparsers.add_parser("folder", help="微盘目录相关命令")
    space_folder_subparsers = add_required_subparsers(
        space_folder_parser, dest="space_folder_command"
    )
    space_folder_create_parser = space_folder_subparsers.add_parser(
        "create", help="根据 YAML 模板在已有空间或目录下创建目录"
    )
    space_folder_create_parser.add_argument("template_path", help="目录模板路径")
    add_auth_args(space_folder_create_parser)

    space_admin_parser = space_subparsers.add_parser("admin", help="空间管理员相关命令")
    space_admin_subparsers = add_required_subparsers(
        space_admin_parser, dest="space_admin_command"
    )
    space_admin_add_parser = space_admin_subparsers.add_parser(
        "add", help="根据 YAML 模板给已有空间添加管理员"
    )
    space_admin_add_parser.add_argument("template_path", help="空间管理员模板路径")
    add_auth_args(space_admin_add_parser)

    smartsheet_parser = subparsers.add_parser("smartsheet", help="智能表格相关命令")
    smartsheet_subparsers = add_required_subparsers(
        smartsheet_parser, dest="smartsheet_command"
    )
    smartsheet_create_parser = smartsheet_subparsers.add_parser(
        "create", help="根据 YAML 模板创建智能表格"
    )
    smartsheet_create_parser.add_argument("template_path", help="智能表格模板路径")
    add_auth_args(smartsheet_create_parser)

    smartsheet_sheet_parser = smartsheet_subparsers.add_parser(
        "sheet", help="智能表格子表相关命令"
    )
    smartsheet_sheet_subparsers = add_required_subparsers(
        smartsheet_sheet_parser, dest="smartsheet_sheet_command"
    )
    smartsheet_sheet_create_parser = smartsheet_sheet_subparsers.add_parser(
        "create", help="根据 YAML 模板在已有智能表格中创建子表"
    )
    smartsheet_sheet_create_parser.add_argument("template_path", help="子表模板路径")
    add_auth_args(smartsheet_sheet_create_parser)

    doc_parser = subparsers.add_parser("doc", help="文档权限相关命令")
    doc_subparsers = add_required_subparsers(doc_parser, dest="doc_command")
    doc_admin_parser = doc_subparsers.add_parser("admin", help="文档管理员相关命令")
    doc_admin_subparsers = add_required_subparsers(
        doc_admin_parser, dest="doc_admin_command"
    )
    doc_admin_add_parser = doc_admin_subparsers.add_parser(
        "add", help="根据 YAML 模板给已有文档添加管理员"
    )
    doc_admin_add_parser.add_argument("template_path", help="文档管理员模板路径")
    add_auth_args(doc_admin_add_parser)

    return parser


def main(argv: list[str] | None = None) -> int:
    """CLI 入口。"""

    parser = build_parser()
    try:
        args = parser.parse_args(argv)
    except CLIArgumentParserExit as exc:
        return exc.status

    try:
        if args.command == "template":
            if args.template_command == "init":
                run_template_init(
                    kind=args.template_kind,
                    template_path=Path(args.template_path),
                    mode=getattr(args, "mode", TEMPLATE_MODE_CREATE),
                )
                return 0

        if args.command == "space":
            if args.space_command == "create":
                run_space_create(
                    corp_id=args.corp_id,
                    corp_secret=args.corp_secret,
                    template_path=args.template_path,
                )
                return 0
            if args.space_command == "folder" and args.space_folder_command == "create":
                run_space_folder_create(
                    corp_id=args.corp_id,
                    corp_secret=args.corp_secret,
                    template_path=args.template_path,
                )
                return 0
            if args.space_command == "admin" and args.space_admin_command == "add":
                run_space_admin_add(
                    corp_id=args.corp_id,
                    corp_secret=args.corp_secret,
                    template_path=args.template_path,
                )
                return 0

        if args.command == "smartsheet":
            if args.smartsheet_command == "create":
                run_smartsheet_create(
                    corp_id=args.corp_id,
                    corp_secret=args.corp_secret,
                    template_path=args.template_path,
                )
                return 0
            if (
                args.smartsheet_command == "sheet"
                and args.smartsheet_sheet_command == "create"
            ):
                run_smartsheet_sheet_create(
                    corp_id=args.corp_id,
                    corp_secret=args.corp_secret,
                    template_path=args.template_path,
                )
                return 0

        if args.command == "doc":
            if args.doc_command == "admin" and args.doc_admin_command == "add":
                run_doc_admin_add(
                    corp_id=args.corp_id,
                    corp_secret=args.corp_secret,
                    template_path=args.template_path,
                )
                return 0

        if args.command == "scaffold":
            run_scaffold(
                corp_id=args.corp_id,
                corp_secret=args.corp_secret,
                template_path=Path(args.template_path),
                output_path=Path(args.output) if args.output else None,
                dry_run=bool(args.dry_run),
            )
            return 0
    except CLIError as exc:
        print(str(exc), file=sys.stderr)
        return 1

    return 1
