from __future__ import annotations

import json
from pathlib import Path

from wecom_doc_sdk.cli import main


def test_template_init_success_payload_has_no_mode(
    tmp_path: Path,
    capsys,
) -> None:
    """template init 成功输出不再包含 mode 字段。"""

    output_path = tmp_path / "space.yaml"

    exit_code = main(["template", "init", "space", str(output_path)])

    payload = json.loads(capsys.readouterr().out)

    assert exit_code == 0
    assert payload["status"] == "success"
    assert payload["action"] == "template_init"
    assert payload["kind"] == "space"
    assert payload["path"] == str(output_path.resolve())
    assert "mode" not in payload


def test_template_init_generates_resource_templates(
    tmp_path: Path,
) -> None:
    """template init 应支持六类资源模板。"""

    cases = [
        (
            "space",
            "space.yaml",
            "这份模板可直接交给 `wecom-doc-sdk space create` 使用。",
        ),
        (
            "folder",
            "folder.yaml",
            "这份模板可直接交给 `wecom-doc-sdk space folder create` 使用。",
        ),
        (
            "smartsheet",
            "smartsheet.yaml",
            "这份模板可直接交给 `wecom-doc-sdk smartsheet create` 使用。",
        ),
        (
            "sheet",
            "sheet.yaml",
            "这份模板可直接交给 `wecom-doc-sdk smartsheet sheet create` 使用。",
        ),
        (
            "space-admin",
            "space-admin.yaml",
            "这份模板可直接交给 `wecom-doc-sdk space admin add` 使用。",
        ),
        (
            "doc-admin",
            "doc-admin.yaml",
            "这份模板可直接交给 `wecom-doc-sdk doc admin add` 使用。",
        ),
    ]

    for kind, file_name, expected_text in cases:
        output_path = tmp_path / file_name
        exit_code = main(["template", "init", kind, str(output_path)])
        content = output_path.read_text(encoding="utf-8")
        assert exit_code == 0
        assert expected_text in content


def test_template_init_uses_incremented_name_when_output_exists(tmp_path: Path) -> None:
    """目标路径已存在时应自动生成带序号的新文件。"""

    output_path = tmp_path / "space.yaml"
    output_path.write_text("existing\n", encoding="utf-8")

    exit_code = main(["template", "init", "space", str(output_path)])

    incremented_path = tmp_path / "space.1.yaml"

    assert exit_code == 0
    assert output_path.read_text(encoding="utf-8") == "existing\n"
    assert incremented_path.exists()


def test_template_init_rejects_mode_argument(tmp_path: Path, capsys) -> None:
    """template init 不再接受 --mode。"""

    output_path = tmp_path / "space.yaml"

    exit_code = main(
        [
            "template",
            "init",
            "space",
            str(output_path),
            "--mode",
            "use_existing",
        ]
    )

    captured = capsys.readouterr()

    assert exit_code == 2
    assert "usage: wecom-doc-sdk" in captured.err
    assert "unrecognized arguments: --mode use_existing" in captured.err


def test_cli_reports_nested_help_for_missing_subcommands(capsys) -> None:
    """缺少子命令时应输出当前层级帮助。"""

    cases = [
        (["template"], "usage: wecom-doc-sdk template"),
        (["template", "init"], "usage: wecom-doc-sdk template init"),
        (["space"], "usage: wecom-doc-sdk space"),
        (["space", "folder"], "usage: wecom-doc-sdk space folder"),
        (["smartsheet"], "usage: wecom-doc-sdk smartsheet"),
        (["smartsheet", "sheet"], "usage: wecom-doc-sdk smartsheet sheet"),
        (["doc"], "usage: wecom-doc-sdk doc"),
        (["doc", "admin"], "usage: wecom-doc-sdk doc admin"),
    ]

    for argv, expected_usage in cases:
        exit_code = main(argv)
        captured = capsys.readouterr()
        assert exit_code == 2
        assert expected_usage in captured.err
