from __future__ import annotations

import json
from pathlib import Path
from typing import Any

import pytest

from wecom_doc_sdk.cli import main

from .helpers import (
    FakeWeComClient,
    build_sheet_template,
    build_smartsheet_template,
    install_fake_yaml,
    patch_wecom_client,
    write_template_file,
)


def test_smartsheet_create_outputs_json(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
    capsys: pytest.CaptureFixture[str],
) -> None:
    """smartsheet create 应仅创建智能表格。"""

    template_path = write_template_file(tmp_path, "smartsheet.yaml")
    install_fake_yaml(monkeypatch, build_smartsheet_template())
    FakeWeComClient.instances.clear()
    patch_wecom_client(monkeypatch, FakeWeComClient)

    exit_code = main(
        [
            "smartsheet",
            "create",
            str(template_path),
            "--corp-id",
            "corp-id",
            "--corp-secret",
            "corp-secret",
        ]
    )

    payload = json.loads(capsys.readouterr().out)
    calls = FakeWeComClient.instances[0].calls

    assert exit_code == 0
    assert [name for name, _ in calls] == ["create_doc"]
    assert payload["docid"] == "DOCID-1"
    assert payload["title"] == "项目主表"
    assert payload["spaceid"] == "SPACEID"
    assert payload["fatherid"] == "FOLDERID"



def test_smartsheet_create_with_sheet_and_fields(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
    capsys: pytest.CaptureFixture[str],
) -> None:
    """smartsheet create 带 sheet 时应继续创建子表和字段。"""

    template_path = write_template_file(tmp_path, "smartsheet.yaml")
    install_fake_yaml(monkeypatch, build_smartsheet_template(with_sheet=True))
    FakeWeComClient.instances.clear()
    patch_wecom_client(monkeypatch, FakeWeComClient)

    exit_code = main(
        [
            "smartsheet",
            "create",
            str(template_path),
            "--corp-id",
            "corp-id",
            "--corp-secret",
            "corp-secret",
        ]
    )

    payload = json.loads(capsys.readouterr().out)
    calls = FakeWeComClient.instances[0].calls

    assert exit_code == 0
    assert [name for name, _ in calls] == ["create_doc", "add_sheet", "add_fields"]
    assert payload["sheet"]["sheet_id"] == "SHEETID-1"
    assert payload["sheet"]["fields"][0]["field_title"] == "文件名"



def test_smartsheet_sheet_create_with_fields(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
    capsys: pytest.CaptureFixture[str],
) -> None:
    """smartsheet sheet create 应在已有 doc 下创建子表和字段。"""

    template_path = write_template_file(tmp_path, "sheet.yaml")
    install_fake_yaml(monkeypatch, build_sheet_template(with_fields=True))
    FakeWeComClient.instances.clear()
    patch_wecom_client(monkeypatch, FakeWeComClient)

    exit_code = main(
        [
            "smartsheet",
            "sheet",
            "create",
            str(template_path),
            "--corp-id",
            "corp-id",
            "--corp-secret",
            "corp-secret",
        ]
    )

    payload = json.loads(capsys.readouterr().out)
    calls = FakeWeComClient.instances[0].calls

    assert exit_code == 0
    assert [name for name, _ in calls] == ["add_sheet", "add_fields"]
    assert payload["docid"] == "DOCID"
    assert payload["sheet_id"] == "SHEETID-1"
    assert payload["fields"][1]["field_type"] == "FIELD_TYPE_ATTACHMENT"


@pytest.mark.parametrize(
    ("command", "payload", "expected_error"),
    [
        (["smartsheet", "create"], {"spaceid": "SPACEID"}, "title"),
        (["smartsheet", "sheet", "create"], {"title": "附件表"}, "docid"),
    ],
)
def test_smartsheet_commands_report_template_validation_error(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
    capsys: pytest.CaptureFixture[str],
    command: list[str],
    payload: dict[str, Any],
    expected_error: str,
) -> None:
    """智能表格模板缺字段时应报模板校验失败。"""

    template_path = write_template_file(tmp_path)
    install_fake_yaml(monkeypatch, payload)

    exit_code = main(
        command
        + [
            str(template_path),
            "--corp-id",
            "corp-id",
            "--corp-secret",
            "corp-secret",
        ]
    )

    captured = capsys.readouterr()

    assert exit_code == 1
    assert "模板校验失败" in captured.err
    assert expected_error in captured.err
