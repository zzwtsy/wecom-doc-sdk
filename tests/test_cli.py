from __future__ import annotations

import json
import sys
from pathlib import Path
from types import SimpleNamespace
from typing import Any

import pytest

from wecom_doc_sdk import cli
from wecom_doc_sdk.models.documents import CreateDocResponse
from wecom_doc_sdk.models.enums import FieldType
from wecom_doc_sdk.models.fields import AddFieldsResponse, FieldModel
from wecom_doc_sdk.models.sheets import AddSheetResponse, SheetProperties
from wecom_doc_sdk.models.uploads import CreateFileResponse, CreateSpaceResponse


def install_fake_yaml(
    monkeypatch: pytest.MonkeyPatch, payload: dict[str, Any] | list[Any] | None
) -> None:
    """注入假的 yaml 模块，避免测试依赖真实 PyYAML。"""

    fake_yaml = SimpleNamespace(safe_load=lambda text: payload)
    monkeypatch.setitem(sys.modules, "yaml", fake_yaml)


def write_template_file(tmp_path: Path) -> Path:
    """写入一个占位模板文件。"""

    template_path = tmp_path / "template.yaml"
    template_path.write_text("template: ignored\n", encoding="utf-8")
    return template_path


def build_create_template() -> dict[str, Any]:
    """生成 create 模式模板。"""

    return {
        "wedrive": {
            "mode": "create",
            "space_name": "项目资料库",
            "space_sub_type": 0,
            "auth_info": [{"type": 1, "userid": "zhangsan", "auth": 7}],
            "folder_name": "附件目录",
        },
        "doc": {"title": "项目主表"},
        "sheets": [
            {
                "title": "附件表",
                "fields": [
                    {
                        "field_title": "文件名",
                        "field_type": FieldType.FIELD_TYPE_TEXT.value,
                    },
                    {
                        "field_title": "附件",
                        "field_type": FieldType.FIELD_TYPE_ATTACHMENT.value,
                    },
                ],
            }
        ],
    }


def build_existing_template() -> dict[str, Any]:
    """生成 use_existing 模式模板。"""

    return {
        "wedrive": {
            "mode": "use_existing",
            "spaceid": "SPACEID",
            "fatherid": "FOLDERID",
        },
        "doc": {"title": "已有空间主表"},
        "sheets": [
            {
                "title": "收集表",
                "fields": [
                    {
                        "field_title": "标题",
                        "field_type": FieldType.FIELD_TYPE_TEXT.value,
                    }
                ],
            }
        ],
    }


class FakeUploadsAPI:
    """记录微盘 API 调用。"""

    def __init__(self, calls: list[tuple[str, dict[str, Any]]]) -> None:
        self._calls = calls

    def create_space(self, request: Any) -> CreateSpaceResponse:
        payload = request.model_dump(exclude_none=True)
        self._calls.append(("create_space", payload))
        return CreateSpaceResponse(errcode=0, errmsg="ok", spaceid="SPACEID")

    def create_file(self, request: Any) -> CreateFileResponse:
        payload = request.model_dump(exclude_none=True)
        self._calls.append(("create_file", payload))
        return CreateFileResponse(errcode=0, errmsg="ok", fileid="FOLDERID")


class FakeDocumentsAPI:
    """记录文档 API 调用。"""

    def __init__(self, calls: list[tuple[str, dict[str, Any]]]) -> None:
        self._calls = calls

    def create_doc(self, request: Any) -> CreateDocResponse:
        payload = request.model_dump(exclude_none=True)
        self._calls.append(("create_doc", payload))
        return CreateDocResponse(errcode=0, errmsg="ok", docid="DOCID")


class FakeSmartSheetAPI:
    """记录智能表格 API 调用。"""

    def __init__(self, calls: list[tuple[str, dict[str, Any]]]) -> None:
        self._calls = calls

    def add_sheet(self, request: Any) -> AddSheetResponse:
        payload = request.model_dump(exclude_none=True)
        self._calls.append(("add_sheet", payload))
        return AddSheetResponse(
            errcode=0,
            errmsg="ok",
            properties=SheetProperties(sheet_id="SHEETID", title="附件表", index=0),
        )

    def add_fields(self, request: Any) -> AddFieldsResponse:
        payload = request.model_dump(exclude_none=True)
        self._calls.append(("add_fields", payload))
        return AddFieldsResponse(
            errcode=0,
            errmsg="ok",
            fields=[
                FieldModel(
                    field_id="FIELD-1",
                    field_title="文件名",
                    field_type=FieldType.FIELD_TYPE_TEXT,
                ),
                FieldModel(
                    field_id="FIELD-2",
                    field_title="附件",
                    field_type=FieldType.FIELD_TYPE_ATTACHMENT,
                ),
            ],
        )


class FakeWeComClient:
    """用于 CLI 测试的假客户端。"""

    instances: list["FakeWeComClient"] = []

    def __init__(self, corp_id: str, corp_secret: str) -> None:
        self.corp_id = corp_id
        self.corp_secret = corp_secret
        self.calls: list[tuple[str, dict[str, Any]]] = []
        self.uploads = FakeUploadsAPI(self.calls)
        self.documents = FakeDocumentsAPI(self.calls)
        self.smartsheet = FakeSmartSheetAPI(self.calls)
        FakeWeComClient.instances.append(self)

    def __enter__(self) -> "FakeWeComClient":
        return self

    def __exit__(self, exc_type, exc, tb) -> None:
        return None


def test_init_template_creates_default_create_mode_yaml(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
    capsys: pytest.CaptureFixture[str],
) -> None:
    """init-template 默认应生成带注释的 create 模式模板。"""

    output_path = tmp_path / "template.yaml"

    def fail_if_client_created(*args: Any, **kwargs: Any) -> None:
        raise AssertionError("init-template 不应初始化 WeComClient")

    monkeypatch.setattr(cli, "WeComClient", fail_if_client_created)

    exit_code = cli.main(["init-template", str(output_path)])

    captured = capsys.readouterr()
    content = output_path.read_text(encoding="utf-8")

    assert exit_code == 0
    assert "已生成模板" in captured.out
    assert "# 企业微信智能表格脚手架模板。" in content
    assert "# 这份模板可以直接交给 `wecom-doc-sdk scaffold` 使用。" in content
    assert "mode: create" in content
    assert "space_name: 示例空间" in content
    assert "folder_name: 附件目录" in content
    assert "# auth_info:" in content
    assert "#   # `type` 表示授权对象类型：1=成员，2=部门。" in content
    assert "#     # `auth` 表示权限：1=仅下载，4=可预览，7=应用空间管理员。" in content
    assert "字段定义列表；列表中的每一项都会创建成一个字段" in content
    assert "`field_title` 是字段显示名称，`field_type` 是字段类型枚举值。" in content
    assert "可以继续补充对应的 `property_*` 配置。" in content
    assert "field_type: FIELD_TYPE_ATTACHMENT" in content
    assert "你可以继续在 sheets 下追加更多子表。" in content


def test_init_template_supports_use_existing_mode(
    tmp_path: Path,
) -> None:
    """init-template 应支持生成 use_existing 模式模板。"""

    output_path = tmp_path / "existing-template.yaml"

    exit_code = cli.main(
        ["init-template", str(output_path), "--mode", "use_existing"]
    )

    content = output_path.read_text(encoding="utf-8")

    assert exit_code == 0
    assert "mode: use_existing" in content
    assert "spaceid: SPACEID" in content
    assert "fatherid: FOLDERID" in content
    assert "space_name: 示例空间" not in content


def test_init_template_uses_incremented_name_when_target_exists(
    tmp_path: Path,
    capsys: pytest.CaptureFixture[str],
) -> None:
    """模板输出文件已存在时应自动生成不冲突的新文件名。"""

    output_path = tmp_path / "template.yaml"
    output_path.write_text("existing\n", encoding="utf-8")

    exit_code = cli.main(["init-template", str(output_path)])

    captured = capsys.readouterr()
    incremented_path = tmp_path / "template.1.yaml"

    assert exit_code == 0
    assert output_path.read_text(encoding="utf-8") == "existing\n"
    assert incremented_path.exists()
    assert str(incremented_path) in captured.out


def test_scaffold_dry_run_outputs_plan_without_creating_client(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
    capsys: pytest.CaptureFixture[str],
) -> None:
    """dry-run 应只输出计划，不创建客户端。"""

    template_path = write_template_file(tmp_path)
    install_fake_yaml(monkeypatch, build_create_template())
    FakeWeComClient.instances.clear()
    monkeypatch.setattr(cli, "WeComClient", FakeWeComClient)

    exit_code = cli.main(
        [
            "scaffold",
            str(template_path),
            "--corp-id",
            "corp-id",
            "--corp-secret",
            "corp-secret",
            "--dry-run",
        ]
    )

    captured = capsys.readouterr()
    payload = json.loads(captured.out)

    assert exit_code == 0
    assert FakeWeComClient.instances == []
    assert payload["mode"] == "dry-run"
    assert payload["actions"][0]["step"] == "create_space"
    assert payload["actions"][1]["step"] == "create_folder"


def test_scaffold_create_mode_creates_wedrive_doc_and_manifest(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """create 模式应依次创建空间、目录、文档、子表和字段。"""

    template_path = write_template_file(tmp_path)
    install_fake_yaml(monkeypatch, build_create_template())
    FakeWeComClient.instances.clear()
    monkeypatch.setattr(cli, "WeComClient", FakeWeComClient)

    output_path = tmp_path / "result.json"
    exit_code = cli.main(
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

    manifest = json.loads(output_path.read_text(encoding="utf-8"))
    calls = FakeWeComClient.instances[0].calls

    assert exit_code == 0
    assert [name for name, _ in calls] == [
        "create_space",
        "create_file",
        "create_doc",
        "add_sheet",
        "add_fields",
    ]
    assert manifest["wedrive"] == {"spaceid": "SPACEID", "fatherid": "FOLDERID"}
    assert manifest["doc"] == {"docid": "DOCID", "title": "项目主表"}
    assert manifest["sheets"][0]["sheet_id"] == "SHEETID"
    assert manifest["sheets"][0]["fields"]["文件名"]["field_id"] == "FIELD-1"
    assert (
        manifest["sheets"][0]["fields"]["附件"]["field_type"]
        == "FIELD_TYPE_ATTACHMENT"
    )


def test_scaffold_use_existing_mode_skips_space_creation(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """use_existing 模式不应再创建空间和目录。"""

    template_path = write_template_file(tmp_path)
    install_fake_yaml(monkeypatch, build_existing_template())
    FakeWeComClient.instances.clear()
    monkeypatch.setattr(cli, "WeComClient", FakeWeComClient)

    exit_code = cli.main(
        [
            "scaffold",
            str(template_path),
            "--corp-id",
            "corp-id",
            "--corp-secret",
            "corp-secret",
        ]
    )

    calls = FakeWeComClient.instances[0].calls

    assert exit_code == 0
    assert [name for name, _ in calls] == ["create_doc", "add_sheet", "add_fields"]
    assert calls[0][1]["spaceid"] == "SPACEID"
    assert calls[0][1]["fatherid"] == "FOLDERID"


def test_scaffold_uses_incremented_manifest_name_when_output_exists(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """输出文件已存在时应自动生成不冲突的新文件名。"""

    template_path = write_template_file(tmp_path)
    install_fake_yaml(monkeypatch, build_create_template())
    FakeWeComClient.instances.clear()
    monkeypatch.setattr(cli, "WeComClient", FakeWeComClient)

    output_path = tmp_path / "result.json"
    output_path.write_text("existing\n", encoding="utf-8")

    exit_code = cli.main(
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

    incremented_path = tmp_path / "result.1.json"

    assert exit_code == 0
    assert output_path.read_text(encoding="utf-8") == "existing\n"
    assert incremented_path.exists()


def test_scaffold_reports_template_validation_error(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
    capsys: pytest.CaptureFixture[str],
) -> None:
    """模板缺少关键字段时应返回清晰错误。"""

    template_path = write_template_file(tmp_path)
    invalid_template = build_create_template()
    invalid_template["wedrive"].pop("mode")
    install_fake_yaml(monkeypatch, invalid_template)

    exit_code = cli.main(
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
    invalid_template = build_create_template()
    invalid_template["sheets"][0]["fields"] = [{"field_title": "文件名"}]
    install_fake_yaml(monkeypatch, invalid_template)

    exit_code = cli.main(
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
    install_fake_yaml(monkeypatch, build_create_template())

    class BrokenUploadsAPI(FakeUploadsAPI):
        def create_space(self, request: Any) -> CreateSpaceResponse:
            payload = request.model_dump(exclude_none=True)
            self._calls.append(("create_space", payload))
            return CreateSpaceResponse(errcode=0, errmsg="ok", spaceid=None)

    class BrokenWeComClient(FakeWeComClient):
        def __init__(self, corp_id: str, corp_secret: str) -> None:
            super().__init__(corp_id, corp_secret)
            self.uploads = BrokenUploadsAPI(self.calls)

    monkeypatch.setattr(cli, "WeComClient", BrokenWeComClient)

    exit_code = cli.main(
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
