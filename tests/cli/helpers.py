from __future__ import annotations

import sys
from pathlib import Path
from types import SimpleNamespace
from typing import Any

import pytest

from wecom_doc_sdk.cli.commands import doc as doc_command
from wecom_doc_sdk.cli.commands import smartsheet, space
from wecom_doc_sdk.models.documents import CreateDocResponse
from wecom_doc_sdk.models.enums import FieldType
from wecom_doc_sdk.models.fields import AddFieldsResponse, FieldModel
from wecom_doc_sdk.models.permissions import ModifyDocMemberResponse
from wecom_doc_sdk.models.sheets import AddSheetResponse, SheetProperties
from wecom_doc_sdk.models.uploads import (
    AddSpaceAclResponse,
    CreateFileResponse,
    CreateSpaceResponse,
    GetSpaceInfoResponse,
    SpaceAuthList,
    SpaceInfo,
)


def install_fake_yaml(
    monkeypatch: pytest.MonkeyPatch, payload: dict[str, Any] | list[Any] | None
) -> None:
    """注入假的 yaml 模块，避免测试依赖真实 PyYAML。"""

    fake_yaml = SimpleNamespace(safe_load=lambda text: payload)
    monkeypatch.setitem(sys.modules, "yaml", fake_yaml)


def write_template_file(tmp_path: Path, name: str = "template.yaml") -> Path:
    """写入一个占位模板文件。"""

    template_path = tmp_path / name
    template_path.write_text("template: ignored\n", encoding="utf-8")
    return template_path


def build_space_template(with_folder: bool = False) -> dict[str, Any]:
    """生成空间模板。"""

    payload: dict[str, Any] = {
        "space_name": "项目空间",
        "space_sub_type": 0,
        "auth_info": [{"type": 1, "userid": "zhangsan", "auth": 7}],
    }
    if with_folder:
        payload["folder"] = {"name": "附件目录"}
    return payload


def build_folder_template() -> dict[str, Any]:
    """生成目录模板。"""

    return {
        "spaceid": "SPACEID",
        "fatherid": "FOLDERID",
        "name": "新目录",
    }


def build_smartsheet_template(with_sheets: bool = False) -> dict[str, Any]:
    """生成智能表格模板。"""

    payload: dict[str, Any] = {
        "title": "项目主表",
        "spaceid": "SPACEID",
        "fatherid": "FOLDERID",
        "admin_users": ["zhangsan"],
    }
    if with_sheets:
        payload["sheets"] = [
            {
                "title": "附件表",
                "index": 1,
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
        ]
    return payload


def build_sheet_template(with_fields: bool = False) -> dict[str, Any]:
    """生成子表模板。"""

    payload: dict[str, Any] = {
        "docid": "DOCID",
        "title": "附件表",
        "index": 2,
    }
    if with_fields:
        payload["fields"] = [
            {
                "field_title": "文件名",
                "field_type": FieldType.FIELD_TYPE_TEXT.value,
            },
            {
                "field_title": "附件",
                "field_type": FieldType.FIELD_TYPE_ATTACHMENT.value,
            },
        ]
    return payload


def build_space_admin_template() -> dict[str, Any]:
    """生成空间管理员添加模板。"""

    return {
        "spaceid": "SPACEID",
        "admin_users": ["zhangsan", "lisi"],
    }


def build_doc_admin_template() -> dict[str, Any]:
    """生成文档管理员添加模板。"""

    return {
        "docid": "DOCID",
        "admin_users": ["zhangsan", "lisi"],
    }


class FakeUploadsAPI:
    """记录微盘 API 调用。"""

    def __init__(self, calls: list[tuple[str, dict[str, Any]]]) -> None:
        self._calls = calls
        self._file_counter = 0

    def create_space(self, request: Any) -> CreateSpaceResponse:
        payload = request.model_dump(exclude_none=True)
        self._calls.append(("create_space", payload))
        return CreateSpaceResponse(errcode=0, errmsg="ok", spaceid="SPACEID")

    def create_file(self, request: Any) -> CreateFileResponse:
        payload = request.model_dump(exclude_none=True)
        self._calls.append(("create_file", payload))
        self._file_counter += 1
        return CreateFileResponse(
            errcode=0,
            errmsg="ok",
            fileid=f"FILEID-{self._file_counter}",
        )

    def get_space_info(self, request: Any) -> GetSpaceInfoResponse:
        payload = request.model_dump(exclude_none=True)
        self._calls.append(("get_space_info", payload))
        return GetSpaceInfoResponse(
            errcode=0,
            errmsg="ok",
            space_info=SpaceInfo(
                spaceid=payload["spaceid"],
                auth_list=SpaceAuthList(auth_info=[]),
            ),
        )

    def add_space_acl(self, request: Any) -> AddSpaceAclResponse:
        payload = request.model_dump(exclude_none=True)
        self._calls.append(("add_space_acl", payload))
        return AddSpaceAclResponse(errcode=0, errmsg="ok")


class FakeDocumentsAPI:
    """记录文档 API 调用。"""

    def __init__(self, calls: list[tuple[str, dict[str, Any]]]) -> None:
        self._calls = calls
        self._doc_counter = 0

    def create_doc(self, request: Any) -> CreateDocResponse:
        payload = request.model_dump(exclude_none=True)
        self._calls.append(("create_doc", payload))
        self._doc_counter += 1
        return CreateDocResponse(
            errcode=0,
            errmsg="ok",
            docid=f"DOCID-{self._doc_counter}",
            url=f"https://doc.weixin.qq.com/smartsheet/{self._doc_counter}",
        )


class FakeSmartSheetAPI:
    """记录智能表格 API 调用。"""

    def __init__(self, calls: list[tuple[str, dict[str, Any]]]) -> None:
        self._calls = calls
        self._sheet_counter = 0
        self._field_counter = 0

    def add_sheet(self, request: Any) -> AddSheetResponse:
        payload = request.model_dump(exclude_none=True)
        self._calls.append(("add_sheet", payload))
        self._sheet_counter += 1
        properties = payload.get("properties", {})
        return AddSheetResponse(
            errcode=0,
            errmsg="ok",
            properties=SheetProperties(
                sheet_id=f"SHEETID-{self._sheet_counter}",
                title=properties.get("title"),
                index=properties.get("index"),
            ),
        )

    def add_fields(self, request: Any) -> AddFieldsResponse:
        payload = request.model_dump(exclude_none=True)
        self._calls.append(("add_fields", payload))
        fields: list[FieldModel] = []
        for field_payload in payload.get("fields", []):
            self._field_counter += 1
            fields.append(
                FieldModel(
                    field_id=f"FIELD-{self._field_counter}",
                    field_title=field_payload["field_title"],
                    field_type=FieldType(field_payload["field_type"]),
                )
            )
        return AddFieldsResponse(errcode=0, errmsg="ok", fields=fields)


class FakePermissionsAPI:
    """记录文档权限 API 调用。"""

    def __init__(self, calls: list[tuple[str, dict[str, Any]]]) -> None:
        self._calls = calls

    def modify_doc_member(self, request: Any) -> ModifyDocMemberResponse:
        payload = request.model_dump(exclude_none=True)
        self._calls.append(("modify_doc_member", payload))
        return ModifyDocMemberResponse(errcode=0, errmsg="ok")


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
        self.permissions = FakePermissionsAPI(self.calls)
        FakeWeComClient.instances.append(self)

    def __enter__(self) -> "FakeWeComClient":
        return self

    def __exit__(self, exc_type, exc, tb) -> None:
        return None


def patch_wecom_client(
    monkeypatch: pytest.MonkeyPatch, client_cls: type[FakeWeComClient]
) -> None:
    """把三个资源命令里的客户端统一替换成测试替身。"""

    monkeypatch.setattr(space, "WeComClient", client_cls)
    monkeypatch.setattr(smartsheet, "WeComClient", client_cls)
    monkeypatch.setattr(doc_command, "WeComClient", client_cls)
