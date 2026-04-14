from __future__ import annotations

import argparse
import importlib
import json
from pathlib import Path
from typing import Any

from pydantic import BaseModel, ValidationError

from .errors import CLIError


def _load_yaml_module() -> Any:
    """延迟加载 PyYAML，避免在未安装依赖时导入整个包即失败。"""

    try:
        return importlib.import_module("yaml")
    except ModuleNotFoundError as exc:
        raise CLIError(
            "未安装 PyYAML，无法读取 YAML 模板。"
            "请先执行 `uv sync --dev` 或安装 PyYAML。"
        ) from exc


def load_yaml_payload(template_path: Path | str) -> dict[str, Any]:
    """读取 YAML 模板原始内容。"""

    template_path = Path(template_path)
    if not template_path.exists():
        raise CLIError(f"模板文件不存在：{template_path}")
    if not template_path.is_file():
        raise CLIError(f"模板路径不是文件：{template_path}")

    yaml = _load_yaml_module()
    try:
        payload = yaml.safe_load(template_path.read_text(encoding="utf-8"))
    except Exception as exc:  # pragma: no cover
        raise CLIError(f"读取 YAML 模板失败：{exc}") from exc

    if payload is None:
        raise CLIError("模板文件内容为空")
    if not isinstance(payload, dict):
        raise CLIError("模板顶层必须是对象")
    return payload


def load_template(model_cls: type[BaseModel], template_path: Path | str) -> Any:
    """读取并校验指定模板。"""

    try:
        return model_cls.model_validate(load_yaml_payload(template_path))
    except ValidationError as exc:
        raise CLIError(f"模板校验失败：{exc}") from exc


def resolve_non_conflicting_path(base_path: Path) -> Path:
    """计算不与已有文件冲突的输出路径。"""

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


def print_json(payload: dict[str, Any]) -> None:
    """输出结构化 JSON。"""

    print(json.dumps(payload, ensure_ascii=False, indent=2))


def add_auth_args(parser: argparse.ArgumentParser) -> None:
    """为命令补充企业微信鉴权参数。"""

    parser.add_argument("--corp-id", required=True, help="企业微信 CorpID")
    parser.add_argument("--corp-secret", required=True, help="企业微信应用 Secret")


def require_value(value: str | None, field_name: str, action_name: str) -> str:
    """校验关键响应字段不能为空。"""

    if not value:
        raise CLIError(f"{action_name} 返回缺少 {field_name}")
    return value
