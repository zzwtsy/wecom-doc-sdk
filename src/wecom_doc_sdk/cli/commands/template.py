from __future__ import annotations

from pathlib import Path
from typing import Literal

from ..errors import CLIError
from ..models import TEMPLATE_KIND_SCAFFOLD, TEMPLATE_MODE_CREATE
from ..templates import build_template_content
from ..utils import resolve_non_conflicting_path


def run_template_init(
    *,
    kind: Literal["scaffold", "space", "folder", "smartsheet", "sheet"],
    template_path: Path,
    mode: Literal["create", "use_existing"] = TEMPLATE_MODE_CREATE,
) -> Path:
    """生成带注释的 YAML 模板文件。"""

    if kind != TEMPLATE_KIND_SCAFFOLD and mode != TEMPLATE_MODE_CREATE:
        raise CLIError("只有 scaffold 模板支持 --mode 参数")

    final_path = resolve_non_conflicting_path(template_path)
    final_path.parent.mkdir(parents=True, exist_ok=True)
    final_path.write_text(build_template_content(kind, mode=mode), encoding="utf-8")
    print(f"已生成模板：{final_path}")
    return final_path
