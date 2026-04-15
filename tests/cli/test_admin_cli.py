from __future__ import annotations

import json
from pathlib import Path
from typing import Any

import pytest

from wecom_doc_sdk.cli import main
from wecom_doc_sdk.cli.main import build_parser
from wecom_doc_sdk.models.uploads import (
    CreateSpaceAuthInfo,
    GetSpaceInfoResponse,
    SpaceAuthList,
    SpaceInfo,
)

from .helpers import (
    FakeUploadsAPI,
    FakeWeComClient,
    build_doc_admin_template,
    build_space_admin_template,
    install_fake_yaml,
    patch_wecom_client,
    write_template_file,
)


def test_space_admin_add_outputs_json_and_calls_expected_apis(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
    capsys: pytest.CaptureFixture[str],
) -> None:
    """space admin add 应先查空间信息，再添加管理员。"""

    template_path = write_template_file(tmp_path, "space-admin.yaml")
    payload = build_space_admin_template()
    payload["admin_users"] = [" zhangsan ", "lisi", "zhangsan"]
    install_fake_yaml(monkeypatch, payload)
    FakeWeComClient.instances.clear()
    patch_wecom_client(monkeypatch, FakeWeComClient)

    exit_code = main(
        [
            "space",
            "admin",
            "add",
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
    assert [name for name, _ in calls] == ["get_space_info", "add_space_acl"]
    assert output == {
        "spaceid": "SPACEID",
        "admin_users": ["zhangsan", "lisi"],
        "existing_admin_count": 0,
        "added_count": 2,
        "skipped_existing_admin_users": [],
        "effective_added_count": 2,
    }
    assert calls[1][1] == {
        "spaceid": "SPACEID",
        "auth_info": [
            {"type": 1, "userid": "zhangsan", "auth": 7},
            {"type": 1, "userid": "lisi", "auth": 7},
        ],
    }


def test_doc_admin_add_outputs_json_and_calls_modify_doc_member(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
    capsys: pytest.CaptureFixture[str],
) -> None:
    """doc admin add 应调用 modify_doc_member 添加管理员。"""

    template_path = write_template_file(tmp_path, "doc-admin.yaml")
    payload = build_doc_admin_template()
    payload["admin_users"] = [" zhangsan ", "lisi", "zhangsan"]
    install_fake_yaml(monkeypatch, payload)
    FakeWeComClient.instances.clear()
    patch_wecom_client(monkeypatch, FakeWeComClient)

    exit_code = main(
        [
            "doc",
            "admin",
            "add",
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
    assert [name for name, _ in calls] == ["modify_doc_member"]
    assert output == {
        "docid": "DOCID",
        "admin_users": ["zhangsan", "lisi"],
        "added_count": 2,
    }
    assert calls[0][1] == {
        "docid": "DOCID",
        "update_file_member_list": [
            {"type": 1, "userid": "zhangsan", "auth": 7},
            {"type": 1, "userid": "lisi", "auth": 7},
        ],
    }


def test_space_admin_add_skips_existing_admins_when_checking_limit_and_calling_api(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
    capsys: pytest.CaptureFixture[str],
) -> None:
    """已存在的管理员不应重复计入上限，也不应再次调用添加接口。"""

    template_path = write_template_file(tmp_path, "space-admin.yaml")
    install_fake_yaml(
        monkeypatch,
        {
            "spaceid": "SPACEID",
            "admin_users": ["admin1", "zhangsan"],
        },
    )

    class ExistingAdminUploadsAPI(FakeUploadsAPI):
        def get_space_info(self, request: Any) -> GetSpaceInfoResponse:
            payload = request.model_dump(exclude_none=True)
            self._calls.append(("get_space_info", payload))
            return GetSpaceInfoResponse(
                errcode=0,
                errmsg="ok",
                space_info=SpaceInfo(
                    spaceid=payload["spaceid"],
                    auth_list=SpaceAuthList(
                        auth_info=[
                            CreateSpaceAuthInfo(type=1, userid="admin1", auth=7),
                            CreateSpaceAuthInfo(type=1, userid="admin2", auth=7),
                        ]
                    ),
                ),
            )

    class ExistingAdminWeComClient(FakeWeComClient):
        def __init__(self, corp_id: str, corp_secret: str) -> None:
            super().__init__(corp_id, corp_secret)
            self.uploads = ExistingAdminUploadsAPI(self.calls)

    FakeWeComClient.instances.clear()
    patch_wecom_client(monkeypatch, ExistingAdminWeComClient)

    exit_code = main(
        [
            "space",
            "admin",
            "add",
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
    assert [name for name, _ in calls] == ["get_space_info", "add_space_acl"]
    assert output == {
        "spaceid": "SPACEID",
        "admin_users": ["admin1", "zhangsan"],
        "existing_admin_count": 2,
        "added_count": 2,
        "skipped_existing_admin_users": ["admin1"],
        "effective_added_count": 1,
    }
    assert calls[1][1] == {
        "spaceid": "SPACEID",
        "auth_info": [
            {"type": 1, "userid": "zhangsan", "auth": 7},
        ],
    }


def test_space_admin_add_reports_limit_error(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
    capsys: pytest.CaptureFixture[str],
) -> None:
    """空间现有管理员 + 本次新增超过 3 时应报错。"""

    template_path = write_template_file(tmp_path, "space-admin.yaml")
    install_fake_yaml(
        monkeypatch,
        {
            "spaceid": "SPACEID",
            "admin_users": ["zhangsan", "lisi"],
        },
    )

    class LimitedUploadsAPI(FakeUploadsAPI):
        def get_space_info(self, request: Any) -> GetSpaceInfoResponse:
            payload = request.model_dump(exclude_none=True)
            self._calls.append(("get_space_info", payload))
            return GetSpaceInfoResponse(
                errcode=0,
                errmsg="ok",
                space_info=SpaceInfo(
                    spaceid=payload["spaceid"],
                    auth_list=SpaceAuthList(
                        auth_info=[
                            CreateSpaceAuthInfo(type=1, userid="admin1", auth=7),
                            CreateSpaceAuthInfo(type=1, userid="admin2", auth=7),
                        ]
                    ),
                ),
            )

    class LimitedWeComClient(FakeWeComClient):
        def __init__(self, corp_id: str, corp_secret: str) -> None:
            super().__init__(corp_id, corp_secret)
            self.uploads = LimitedUploadsAPI(self.calls)

    FakeWeComClient.instances.clear()
    patch_wecom_client(monkeypatch, LimitedWeComClient)

    exit_code = main(
        [
            "space",
            "admin",
            "add",
            str(template_path),
            "--corp-id",
            "corp-id",
            "--corp-secret",
            "corp-secret",
        ]
    )

    captured = capsys.readouterr()

    assert exit_code == 1
    assert "应用空间管理员最多 3 人" in captured.err


@pytest.mark.parametrize(
    ("command", "payload", "expected_error"),
    [
        (
            ["space", "admin", "add"],
            {"admin_users": ["zhangsan"]},
            "spaceid",
        ),
        (
            ["doc", "admin", "add"],
            {"docid": "DOCID", "admin_users": []},
            "admin_users",
        ),
        (
            ["doc", "admin", "add"],
            {"docid": "DOCID", "admin_users": ["  "]},
            "admin_users 不能包含空字符串",
        ),
        (
            ["doc", "admin", "add"],
            {
                "docid": "DOCID",
                "admin_users": [f"user{i}" for i in range(101)],
            },
            "最多支持 100",
        ),
    ],
)
def test_admin_commands_report_template_validation_error(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
    capsys: pytest.CaptureFixture[str],
    command: list[str],
    payload: dict[str, Any],
    expected_error: str,
) -> None:
    """管理员模板非法时应返回模板校验错误。"""

    template_path = write_template_file(tmp_path, "admin.yaml")
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


def test_parser_accepts_admin_command_routes() -> None:
    """参数解析器应支持 space/doc 的 admin add 路由。"""

    parser = build_parser()

    space_args = parser.parse_args(
        [
            "space",
            "admin",
            "add",
            "space-admin.yaml",
            "--corp-id",
            "corp-id",
            "--corp-secret",
            "corp-secret",
        ]
    )
    doc_args = parser.parse_args(
        [
            "doc",
            "admin",
            "add",
            "doc-admin.yaml",
            "--corp-id",
            "corp-id",
            "--corp-secret",
            "corp-secret",
        ]
    )

    assert space_args.command == "space"
    assert space_args.space_command == "admin"
    assert space_args.space_admin_command == "add"
    assert doc_args.command == "doc"
    assert doc_args.doc_command == "admin"
    assert doc_args.doc_admin_command == "add"
