from __future__ import annotations

from typing import Any, Iterator

import pytest

from wecom_doc_sdk import WeComClient
from wecom_doc_sdk.apis import PermissionsAPI
from wecom_doc_sdk.models.permissions import (
    CoAuthDepartment,
    CreateSheetPrivRuleRequest,
    DocWatermark,
    GetDocAuthRequest,
    GetSheetPrivRequest,
    ModifyDocJoinRuleRequest,
    ModifyDocSafetySettingRequest,
    ModifySheetPrivRuleMemberRequest,
    SheetPrivFieldPriv,
    SheetPrivFieldRule,
    SheetPrivItem,
    SheetPrivMemberRange,
    SheetPrivRecordPriv,
    SheetPrivRecordRule,
    UpdateSheetPrivRequest,
)


@pytest.fixture
def client() -> Iterator[WeComClient]:
    """提供一个可关闭的 SDK 客户端实例。"""

    sdk_client = WeComClient("corp-id", "corp-secret")
    try:
        yield sdk_client
    finally:
        sdk_client.close()


def _bind_request_json(client: WeComClient, payload: dict[str, Any]) -> dict[str, Any]:
    """替换请求方法，记录本次 API 调用细节。"""

    captured: dict[str, Any] = {}

    def fake_request_json(
        method: str,
        path: str,
        *,
        params: dict[str, Any] | None = None,
        json: dict[str, Any] | None = None,
    ) -> dict[str, Any]:
        captured["method"] = method
        captured["path"] = path
        captured["params"] = params
        captured["json"] = json
        return payload

    client.request_json = fake_request_json  # type: ignore[method-assign]
    return captured


def test_client_mounts_permissions_api(client: WeComClient) -> None:
    """客户端应默认挂载文档权限 API。"""

    assert isinstance(client.permissions, PermissionsAPI)


def test_get_doc_auth_parses_nested_response(client: WeComClient) -> None:
    """获取权限信息应命中正确路径并解析嵌套结构。"""

    captured = _bind_request_json(
        client,
        {
            "errcode": 0,
            "errmsg": "ok",
            "access_rule": {
                "enable_corp_internal": True,
                "corp_internal_auth": 1,
                "enable_corp_external": False,
                "corp_external_auth": 2,
                "corp_internal_approve_only_by_admin": True,
                "corp_external_approve_only_by_admin": True,
                "ban_share_external": True,
            },
            "secure_setting": {
                "enable_readonly_copy": False,
                "enable_readonly_comment": False,
                "watermark": {
                    "margin_type": 2,
                    "show_visitor_name": True,
                    "show_text": True,
                    "text": "internal",
                },
            },
            "doc_member_list": [
                {"type": 1, "userid": "zhangsan", "auth": 7},
                {"type": 1, "tmp_external_userid": "tmp-1", "auth": 1},
            ],
            "co_auth_list": [{"type": 2, "departmentid": 1, "auth": 2}],
        },
    )

    response = client.permissions.get_doc_auth(GetDocAuthRequest(docid="DOCID"))

    assert captured["method"] == "POST"
    assert captured["path"] == "/cgi-bin/wedoc/doc_get_auth"
    assert captured["json"] == {"docid": "DOCID"}
    assert response.access_rule is not None
    assert response.access_rule.enable_corp_internal is True
    assert response.secure_setting is not None
    assert response.secure_setting.watermark is not None
    assert response.secure_setting.watermark.text == "internal"
    assert response.doc_member_list is not None
    assert response.doc_member_list[0].auth == 7
    assert response.co_auth_list is not None
    assert response.co_auth_list[0].departmentid == 1


def test_modify_doc_join_rule_serializes_model_request(client: WeComClient) -> None:
    """修改加入规则应正确序列化部门共权限配置。"""

    captured = _bind_request_json(client, {"errcode": 0, "errmsg": "ok"})

    response = client.permissions.modify_doc_join_rule(
        ModifyDocJoinRuleRequest(
            docid="DOCID",
            enable_corp_internal=True,
            corp_internal_auth=2,
            update_co_auth_list=True,
            co_auth_list=[CoAuthDepartment(type=2, departmentid=10001, auth=1)],
        )
    )

    assert response.ok is True
    assert captured["method"] == "POST"
    assert captured["path"] == "/cgi-bin/wedoc/mod_doc_join_rule"
    assert captured["json"] == {
        "docid": "DOCID",
        "enable_corp_internal": True,
        "corp_internal_auth": 2,
        "update_co_auth_list": True,
        "co_auth_list": [{"type": 2, "departmentid": 10001, "auth": 1}],
    }


def test_modify_doc_member_accepts_dict_request(client: WeComClient) -> None:
    """修改成员与权限应支持直接传入 dict。"""

    captured = _bind_request_json(client, {"errcode": 0, "errmsg": "ok"})

    response = client.permissions.modify_doc_member(
        {
            "docid": "DOCID",
            "update_file_member_list": [
                {"type": 1, "userid": "lisi", "auth": 2},
                {"type": 1, "tmp_external_userid": "tmp-2", "auth": 1},
            ],
            "del_file_member_list": [
                {"type": 1, "userid": "wangwu"},
                {"type": 1, "tmp_external_userid": "tmp-3"},
            ],
        }
    )

    assert response.ok is True
    assert captured["method"] == "POST"
    assert captured["path"] == "/cgi-bin/wedoc/mod_doc_member"
    assert captured["json"] == {
        "docid": "DOCID",
        "update_file_member_list": [
            {"type": 1, "userid": "lisi", "auth": 2},
            {"type": 1, "tmp_external_userid": "tmp-2", "auth": 1},
        ],
        "del_file_member_list": [
            {"type": 1, "userid": "wangwu"},
            {"type": 1, "tmp_external_userid": "tmp-3"},
        ],
    }


def test_modify_doc_safety_setting_uses_official_safty_path(
    client: WeComClient,
) -> None:
    """公开方法名使用 safety，但实际请求路径需保持官方 safty 拼写。"""

    captured = _bind_request_json(client, {"errcode": 0, "errmsg": "ok"})

    response = client.permissions.modify_doc_safety_setting(
        ModifyDocSafetySettingRequest(
            docid="DOCID",
            enable_readonly_copy=False,
            enable_readonly_comment=True,
            watermark=DocWatermark(
                margin_type=1,
                show_visitor_name=True,
                show_text=True,
                text="classified",
            ),
        )
    )

    assert response.ok is True
    assert captured["method"] == "POST"
    assert captured["path"] == "/cgi-bin/wedoc/mod_doc_safty_setting"
    assert captured["json"] == {
        "docid": "DOCID",
        "enable_readonly_copy": False,
        "enable_readonly_comment": True,
        "watermark": {
            "margin_type": 1,
            "show_visitor_name": True,
            "show_text": True,
            "text": "classified",
        },
    }


def test_get_sheet_priv_parses_rule_list(client: WeComClient) -> None:
    """查询智能表权限应命中正确路径并解析规则列表。"""

    captured = _bind_request_json(
        client,
        {
            "errcode": 0,
            "errmsg": "ok",
            "rule_list": [
                {
                    "rule_id": 1,
                    "type": 1,
                    "name": "全员权限",
                    "priv_list": [{"sheet_id": "sheet-1", "priv": 2}],
                }
            ],
        },
    )

    response = client.permissions.get_sheet_priv(
        GetSheetPrivRequest(docid="DOCID", type=1)
    )

    assert response.ok is True
    assert captured["path"] == "/cgi-bin/wedoc/smartsheet/content_priv/get_sheet_priv"
    assert captured["json"] == {"docid": "DOCID", "type": 1}
    assert response.rule_list is not None
    assert response.rule_list[0].name == "全员权限"


def test_update_sheet_priv_serializes_nested_rules(client: WeComClient) -> None:
    """更新智能表权限应正确序列化嵌套字段与记录规则。"""

    captured = _bind_request_json(client, {"errcode": 0, "errmsg": "ok"})

    response = client.permissions.update_sheet_priv(
        UpdateSheetPrivRequest(
            docid="DOCID",
            type=2,
            rule_id=3,
            name="项目组权限",
            priv_list=[
                SheetPrivItem(
                    sheet_id="sheet-1",
                    priv=2,
                    can_insert_record=True,
                    field_priv=SheetPrivFieldPriv(
                        field_range_type=2,
                        field_rule_list=[
                            SheetPrivFieldRule(
                                field_id="field-1",
                                field_type="FIELD_TYPE_TEXT",
                                can_edit=True,
                                can_insert=True,
                                can_view=True,
                            )
                        ],
                    ),
                    record_priv=SheetPrivRecordPriv(
                        record_range_type=2,
                        record_rule_list=[
                            SheetPrivRecordRule(
                                field_id="CREATED_USER",
                                oper_type=1,
                            )
                        ],
                        other_priv=1,
                    ),
                )
            ],
        )
    )

    assert response.ok is True
    assert (
        captured["path"] == "/cgi-bin/wedoc/smartsheet/content_priv/update_sheet_priv"
    )
    assert captured["json"] == {
        "docid": "DOCID",
        "type": 2,
        "rule_id": 3,
        "name": "项目组权限",
        "priv_list": [
            {
                "sheet_id": "sheet-1",
                "priv": 2,
                "can_insert_record": True,
                "field_priv": {
                    "field_range_type": 2,
                    "field_rule_list": [
                        {
                            "field_id": "field-1",
                            "field_type": "FIELD_TYPE_TEXT",
                            "can_edit": True,
                            "can_insert": True,
                            "can_view": True,
                        }
                    ],
                },
                "record_priv": {
                    "record_range_type": 2,
                    "record_rule_list": [{"field_id": "CREATED_USER", "oper_type": 1}],
                    "other_priv": 1,
                },
            }
        ],
    }


def test_sheet_priv_rule_crud_accepts_dict_and_model(client: WeComClient) -> None:
    """额外权限规则增删改成员接口应支持模型与 dict 入参。"""

    captured = _bind_request_json(client, {"errcode": 0, "errmsg": "ok", "rule_id": 9})
    create_resp = client.permissions.create_sheet_priv_rule(
        CreateSheetPrivRuleRequest(docid="DOCID", name="研发组")
    )
    assert create_resp.rule_id == 9
    assert captured["path"] == "/cgi-bin/wedoc/smartsheet/content_priv/create_rule"
    assert captured["json"] == {"docid": "DOCID", "name": "研发组"}

    captured = _bind_request_json(client, {"errcode": 0, "errmsg": "ok"})
    modify_resp = client.permissions.modify_sheet_priv_rule_member(
        ModifySheetPrivRuleMemberRequest(
            docid="DOCID",
            rule_id=9,
            add_member_range=SheetPrivMemberRange(userid_list=["u1"]),
            del_member_range=SheetPrivMemberRange(userid_list=["u2"]),
        )
    )
    assert modify_resp.ok is True
    assert captured["path"] == "/cgi-bin/wedoc/smartsheet/content_priv/mod_rule_member"
    assert captured["json"] == {
        "docid": "DOCID",
        "rule_id": 9,
        "add_member_range": {"userid_list": ["u1"]},
        "del_member_range": {"userid_list": ["u2"]},
    }

    captured = _bind_request_json(client, {"errcode": 0, "errmsg": "ok"})
    delete_resp = client.permissions.delete_sheet_priv_rules(
        {"docid": "DOCID", "rule_id_list": [9]}
    )
    assert delete_resp.ok is True
    assert captured["path"] == "/cgi-bin/wedoc/smartsheet/content_priv/delete_rule"
    assert captured["json"] == {"docid": "DOCID", "rule_id_list": [9]}
