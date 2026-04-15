from __future__ import annotations

import json
from pathlib import Path
from typing import Any

import pytest

from wecom_doc_sdk.cli import main
from wecom_doc_sdk.models.uploads import CreateSpaceResponse

from .helpers import (
    FakeUploadsAPI,
    FakeWeComClient,
    build_scaffold_create_template,
    build_scaffold_existing_template,
    install_fake_yaml,
    patch_wecom_client,
    write_template_file,
)


def test_scaffold_dry_run_outputs_plan_without_creating_client(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
    capsys: pytest.CaptureFixture[str],
) -> None:
    """dry-run 应只输出计划，不创建客户端。"""

    template_path = write_template_file(tmp_path)
    install_fake_yaml(monkeypatch, build_scaffold_create_template())
    FakeWeComClient.instances.clear()
    patch_wecom_client(monkeypatch, FakeWeComClient)

    exit_code = main(
        [
            "scaffold",
            str(template_path),
            "--dry-run",
        ]
    )

    payload = json.loads(capsys.readouterr().out)

    assert exit_code == 0
    assert FakeWeComClient.instances == []
    assert payload["status"] == "success"
    assert payload["action"] == "scaffold"
    assert payload["mode"] == "dry-run"
    assert payload["path"].endswith(".manifest.json")
    assert payload["actions"][0]["step"] == "create_space"
    assert payload["actions"][1]["step"] == "create_folder"



def test_scaffold_create_mode_creates_wedrive_doc_and_manifest(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
    capsys: pytest.CaptureFixture[str],
) -> None:
    """create 模式应依次创建空间、目录、文档、子表和字段。"""

    template_path = write_template_file(tmp_path)
    install_fake_yaml(monkeypatch, build_scaffold_create_template())
    FakeWeComClient.instances.clear()
    patch_wecom_client(monkeypatch, FakeWeComClient)

    output_path = tmp_path / "result.json"
    exit_code = main(
        [
            "scaffold",
            str(template_path),
            "--corp-id",
            "corp-id",
            "--corp-secret",
            "corp-secret",
            "--output",
            str(output_path),
        ]
    )

    output = json.loads(capsys.readouterr().out)
    manifest = json.loads(output_path.read_text(encoding="utf-8"))
    calls = FakeWeComClient.instances[0].calls

    assert exit_code == 0
    assert output == {
        "status": "success",
        "action": "scaffold",
        "path": str(output_path.resolve()),
        "manifest_path": str(output_path.resolve()),
        "template_path": str(template_path.resolve()),
        "spaceid": "SPACEID",
        "fatherid": "FILEID-1",
        "docid": "DOCID-1",
        "sheet_count": 1,
    }
    assert [name for name, _ in calls] == [
        "create_space",
        "create_file",
        "create_doc",
        "add_sheet",
        "add_fields",
    ]
    assert manifest["wedrive"] == {"spaceid": "SPACEID", "fatherid": "FILEID-1"}
    assert manifest["doc"] == {"docid": "DOCID-1", "title": "项目主表"}
    assert manifest["sheets"][0]["sheet_id"] == "SHEETID-1"
    assert manifest["sheets"][0]["fields"]["文件名"]["field_id"] == "FIELD-1"
    assert (
        manifest["sheets"][0]["fields"]["附件"]["field_type"]
        == "FIELD_TYPE_ATTACHMENT"
    )



def test_scaffold_use_existing_mode_skips_space_creation(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
    capsys: pytest.CaptureFixture[str],
) -> None:
    """use_existing 模式不应再创建空间和目录。"""

    template_path = write_template_file(tmp_path)
    install_fake_yaml(monkeypatch, build_scaffold_existing_template())
    FakeWeComClient.instances.clear()
    patch_wecom_client(monkeypatch, FakeWeComClient)

    exit_code = main(
        [
            "scaffold",
            str(template_path),
            "--corp-id",
            "corp-id",
            "--corp-secret",
            "corp-secret",
        ]
    )

    output = json.loads(capsys.readouterr().out)
    calls = FakeWeComClient.instances[0].calls

    assert exit_code == 0
    assert output["status"] == "success"
    assert output["action"] == "scaffold"
    assert output["spaceid"] == "SPACEID"
    assert output["fatherid"] == "FOLDERID"
    assert output["docid"] == "DOCID-1"
    assert [name for name, _ in calls] == ["create_doc", "add_sheet", "add_fields"]
    assert calls[0][1]["spaceid"] == "SPACEID"
    assert calls[0][1]["fatherid"] == "FOLDERID"



def test_scaffold_uses_incremented_manifest_name_when_output_exists(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
    capsys: pytest.CaptureFixture[str],
) -> None:
    """输出文件已存在时应自动生成不冲突的新文件名。"""

    template_path = write_template_file(tmp_path)
    install_fake_yaml(monkeypatch, build_scaffold_create_template())
    FakeWeComClient.instances.clear()
    patch_wecom_client(monkeypatch, FakeWeComClient)

    output_path = tmp_path / "result.json"
    output_path.write_text("existing\n", encoding="utf-8")

    exit_code = main(
        [
            "scaffold",
            str(template_path),
            "--corp-id",
            "corp-id",
            "--corp-secret",
            "corp-secret",
            "--output",
            str(output_path),
        ]
    )

    output = json.loads(capsys.readouterr().out)
    incremented_path = tmp_path / "result.1.json"

    assert exit_code == 0
    assert output["manifest_path"] == str(incremented_path.resolve())
    assert output_path.read_text(encoding="utf-8") == "existing\n"
    assert incremented_path.exists()


def test_scaffold_requires_auth_when_not_dry_run(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
    capsys: pytest.CaptureFixture[str],
) -> None:
    """非 dry-run 缺少鉴权参数时应返回清晰错误。"""

    template_path = write_template_file(tmp_path)
    install_fake_yaml(monkeypatch, build_scaffold_create_template())
    FakeWeComClient.instances.clear()
    patch_wecom_client(monkeypatch, FakeWeComClient)

    exit_code = main(["scaffold", str(template_path)])

    captured = capsys.readouterr()

    assert exit_code == 1
    assert FakeWeComClient.instances == []
    assert "scaffold 缺少鉴权参数" in captured.err
    assert "--corp-id" in captured.err
    assert "--corp-secret" in captured.err



def test_scaffold_reports_template_validation_error(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
    capsys: pytest.CaptureFixture[str],
) -> None:
    """模板缺少关键字段时应返回清晰错误。"""

    template_path = write_template_file(tmp_path)
    invalid_template = build_scaffold_create_template()
    invalid_template["wedrive"].pop("mode")
    install_fake_yaml(monkeypatch, invalid_template)

    exit_code = main(
        [
            "scaffold",
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



def test_scaffold_reports_missing_field_definition(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
    capsys: pytest.CaptureFixture[str],
) -> None:
    """字段缺少必要项时应在模板校验阶段失败。"""

    template_path = write_template_file(tmp_path)
    invalid_template = build_scaffold_create_template()
    invalid_template["sheets"][0]["fields"] = [{"field_title": "文件名"}]
    install_fake_yaml(monkeypatch, invalid_template)

    exit_code = main(
        [
            "scaffold",
            str(template_path),
            "--corp-id",
            "corp-id",
            "--corp-secret",
            "corp-secret",
        ]
    )

    captured = capsys.readouterr()

    assert exit_code == 1
    assert "field_type" in captured.err



def test_scaffold_reports_runtime_error_when_space_creation_missing_spaceid(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
    capsys: pytest.CaptureFixture[str],
) -> None:
    """空间创建响应缺少 spaceid 时应直接失败。"""

    template_path = write_template_file(tmp_path)
    install_fake_yaml(monkeypatch, build_scaffold_create_template())

    class BrokenUploadsAPI(FakeUploadsAPI):
        def create_space(self, request: Any) -> CreateSpaceResponse:
            payload = request.model_dump(exclude_none=True)
            self._calls.append(("create_space", payload))
            return CreateSpaceResponse(errcode=0, errmsg="ok", spaceid=None)

    class BrokenWeComClient(FakeWeComClient):
        def __init__(self, corp_id: str, corp_secret: str) -> None:
            super().__init__(corp_id, corp_secret)
            self.uploads = BrokenUploadsAPI(self.calls)

    patch_wecom_client(monkeypatch, BrokenWeComClient)

    exit_code = main(
        [
            "scaffold",
            str(template_path),
            "--corp-id",
            "corp-id",
            "--corp-secret",
            "corp-secret",
        ]
    )

    captured = capsys.readouterr()

    assert exit_code == 1
    assert "create_space 返回缺少 spaceid" in captured.err
