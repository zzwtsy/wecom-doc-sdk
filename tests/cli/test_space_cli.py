from __future__ import annotations

import json
from pathlib import Path
from typing import Any

import pytest

from wecom_doc_sdk.cli import main

from .helpers import (
    FakeWeComClient,
    build_folder_template,
    build_space_template,
    install_fake_yaml,
    patch_wecom_client,
    write_template_file,
)


def test_space_create_outputs_json(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
    capsys: pytest.CaptureFixture[str],
) -> None:
    """space create 应仅创建空间并输出 JSON。"""

    template_path = write_template_file(tmp_path, "space.yaml")
    install_fake_yaml(monkeypatch, build_space_template())
    FakeWeComClient.instances.clear()
    patch_wecom_client(monkeypatch, FakeWeComClient)

    exit_code = main(
        [
            "space",
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
    assert [name for name, _ in calls] == ["create_space"]
    assert payload == {
        "spaceid": "SPACEID",
        "space_name": "项目空间",
        "space_sub_type": 0,
    }



def test_space_create_with_folder_creates_both_resources(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
    capsys: pytest.CaptureFixture[str],
) -> None:
    """space create 带 folder 时应继续创建目录。"""

    template_path = write_template_file(tmp_path, "space.yaml")
    install_fake_yaml(monkeypatch, build_space_template(with_folder=True))
    FakeWeComClient.instances.clear()
    patch_wecom_client(monkeypatch, FakeWeComClient)

    exit_code = main(
        [
            "space",
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
    assert [name for name, _ in calls] == ["create_space", "create_file"]
    assert payload["folder"] == {"fileid": "FILEID-1", "name": "附件目录"}



def test_space_folder_create_outputs_json(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
    capsys: pytest.CaptureFixture[str],
) -> None:
    """space folder create 应在已有空间下创建目录。"""

    template_path = write_template_file(tmp_path, "folder.yaml")
    install_fake_yaml(monkeypatch, build_folder_template())
    FakeWeComClient.instances.clear()
    patch_wecom_client(monkeypatch, FakeWeComClient)

    exit_code = main(
        [
            "space",
            "folder",
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
    assert [name for name, _ in calls] == ["create_file"]
    assert payload == {
        "spaceid": "SPACEID",
        "fatherid": "FOLDERID",
        "fileid": "FILEID-1",
        "name": "新目录",
    }


@pytest.mark.parametrize(
    ("command", "payload", "expected_error"),
    [
        (["space", "create"], {"space_sub_type": 0}, "space_name"),
        (
            ["space", "folder", "create"],
            {"spaceid": "SPACEID", "name": "新目录"},
            "fatherid",
        ),
    ],
)
def test_space_commands_report_template_validation_error(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
    capsys: pytest.CaptureFixture[str],
    command: list[str],
    payload: dict[str, Any],
    expected_error: str,
) -> None:
    """空间相关模板缺字段时应报模板校验失败。"""

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
