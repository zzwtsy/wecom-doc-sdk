from __future__ import annotations

import argparse
import sys
from pathlib import Path

from .commands.scaffold import run_scaffold
from .commands.smartsheet import run_smartsheet_create, run_smartsheet_sheet_create
from .commands.space import run_space_create, run_space_folder_create
from .commands.template import run_template_init
from .errors import CLIError
from .models import (
    TEMPLATE_KIND_FOLDER,
    TEMPLATE_KIND_SCAFFOLD,
    TEMPLATE_KIND_SHEET,
    TEMPLATE_KIND_SMARTSHEET,
    TEMPLATE_KIND_SPACE,
    TEMPLATE_MODE_CREATE,
    TEMPLATE_MODE_USE_EXISTING,
)
from .utils import add_auth_args


def build_parser() -> argparse.ArgumentParser:
    """构建命令行参数解析器。"""

    parser = argparse.ArgumentParser(prog="wecom-doc-sdk")
    subparsers = parser.add_subparsers(dest="command")

    scaffold_parser = subparsers.add_parser(
        "scaffold", help="根据 YAML 模板创建微盘空间和智能表格"
    )
    scaffold_parser.add_argument("template_path", help="YAML 模板路径")
    add_auth_args(scaffold_parser)
    scaffold_parser.add_argument("--output", help="manifest 输出路径")
    scaffold_parser.add_argument(
        "--dry-run", action="store_true", help="只输出计划，不调用写接口"
    )

    template_parser = subparsers.add_parser("template", help="模板相关命令")
    template_subparsers = template_parser.add_subparsers(dest="template_command")
    template_init_parser = template_subparsers.add_parser(
        "init", help="生成带注释的 YAML 模板"
    )
    template_init_parser.add_argument(
        "kind",
        choices=[
            TEMPLATE_KIND_SCAFFOLD,
            TEMPLATE_KIND_SPACE,
            TEMPLATE_KIND_FOLDER,
            TEMPLATE_KIND_SMARTSHEET,
            TEMPLATE_KIND_SHEET,
        ],
        help="模板类型",
    )
    template_init_parser.add_argument("template_path", help="模板输出路径")
    template_init_parser.add_argument(
        "--mode",
        choices=[TEMPLATE_MODE_CREATE, TEMPLATE_MODE_USE_EXISTING],
        default=TEMPLATE_MODE_CREATE,
        help="仅 scaffold 模板支持，默认 create",
    )

    space_parser = subparsers.add_parser("space", help="微盘空间相关命令")
    space_subparsers = space_parser.add_subparsers(dest="space_command")
    space_create_parser = space_subparsers.add_parser(
        "create", help="根据 YAML 模板创建空间"
    )
    space_create_parser.add_argument("template_path", help="空间模板路径")
    add_auth_args(space_create_parser)

    space_folder_parser = space_subparsers.add_parser(
        "folder", help="微盘目录相关命令"
    )
    space_folder_subparsers = space_folder_parser.add_subparsers(
        dest="space_folder_command"
    )
    space_folder_create_parser = space_folder_subparsers.add_parser(
        "create", help="根据 YAML 模板在已有空间或目录下创建目录"
    )
    space_folder_create_parser.add_argument("template_path", help="目录模板路径")
    add_auth_args(space_folder_create_parser)

    smartsheet_parser = subparsers.add_parser(
        "smartsheet", help="智能表格相关命令"
    )
    smartsheet_subparsers = smartsheet_parser.add_subparsers(
        dest="smartsheet_command"
    )
    smartsheet_create_parser = smartsheet_subparsers.add_parser(
        "create", help="根据 YAML 模板创建智能表格"
    )
    smartsheet_create_parser.add_argument("template_path", help="智能表格模板路径")
    add_auth_args(smartsheet_create_parser)

    smartsheet_sheet_parser = smartsheet_subparsers.add_parser(
        "sheet", help="智能表格子表相关命令"
    )
    smartsheet_sheet_subparsers = smartsheet_sheet_parser.add_subparsers(
        dest="smartsheet_sheet_command"
    )
    smartsheet_sheet_create_parser = smartsheet_sheet_subparsers.add_parser(
        "create", help="根据 YAML 模板在已有智能表格中创建子表"
    )
    smartsheet_sheet_create_parser.add_argument("template_path", help="子表模板路径")
    add_auth_args(smartsheet_sheet_create_parser)

    return parser


def main(argv: list[str] | None = None) -> int:
    """CLI 入口。"""

    parser = build_parser()
    args = parser.parse_args(argv)

    try:
        if args.command == "template":
            if args.template_command == "init":
                run_template_init(
                    kind=args.kind,
                    template_path=Path(args.template_path),
                    mode=args.mode,
                )
                return 0
            parser.print_help()
            return 1

        if args.command == "space":
            if args.space_command == "create":
                run_space_create(
                    corp_id=args.corp_id,
                    corp_secret=args.corp_secret,
                    template_path=args.template_path,
                )
                return 0
            if (
                args.space_command == "folder"
                and args.space_folder_command == "create"
            ):
                run_space_folder_create(
                    corp_id=args.corp_id,
                    corp_secret=args.corp_secret,
                    template_path=args.template_path,
                )
                return 0
            parser.print_help()
            return 1

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
            parser.print_help()
            return 1

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

    parser.print_help()
    return 1
