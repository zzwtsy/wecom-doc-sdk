from __future__ import annotations

from pathlib import Path
from typing import Literal

from ..templates import build_template_content
from ..utils import build_success_payload, print_json, resolve_non_conflicting_path


def run_template_init(
    *,
    kind: Literal[
        "space",
        "folder",
        "smartsheet",
        "sheet",
        "space-admin",
        "doc-admin",
    ],
    template_path: Path,
) -> Path:
    """生成带注释的 YAML 模板文件。"""

    final_path = resolve_non_conflicting_path(template_path)
    final_path.parent.mkdir(parents=True, exist_ok=True)
    final_path.write_text(build_template_content(kind), encoding="utf-8")
    print_json(
        build_success_payload(
            "template_init",
            kind=kind,
            path=str(final_path.resolve()),
        )
    )
    return final_path
