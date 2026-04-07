from __future__ import annotations

from typing import Any, Type, TypeVar

from pydantic import BaseModel

from ..client import WeComClient
from ..models.permissions import (
    CreateSheetPrivRuleRequest,
    CreateSheetPrivRuleResponse,
    DeleteSheetPrivRulesRequest,
    DeleteSheetPrivRulesResponse,
    GetDocAuthRequest,
    GetDocAuthResponse,
    GetSheetPrivRequest,
    GetSheetPrivResponse,
    ModifyDocJoinRuleRequest,
    ModifyDocJoinRuleResponse,
    ModifyDocMemberRequest,
    ModifyDocMemberResponse,
    ModifyDocSafetySettingRequest,
    ModifyDocSafetySettingResponse,
    ModifySheetPrivRuleMemberRequest,
    ModifySheetPrivRuleMemberResponse,
    UpdateSheetPrivRequest,
    UpdateSheetPrivResponse,
)

TModel = TypeVar("TModel", bound=BaseModel)


class PermissionsAPI:
    """设置文档权限相关接口封装。"""

    def __init__(self, client: WeComClient) -> None:
        self._client = client

    @staticmethod
    def _ensure_model(model_cls: Type[TModel], payload: Any) -> TModel:
        if isinstance(payload, model_cls):
            return payload
        return model_cls.model_validate(payload)

    def get_doc_auth(
        self, request: GetDocAuthRequest | dict[str, Any]
    ) -> GetDocAuthResponse:
        """获取文档、表格或智能表格的权限信息。"""
        req = self._ensure_model(GetDocAuthRequest, request)
        data = self._client.request_json(
            "POST",
            "/cgi-bin/wedoc/doc_get_auth",
            json=self._client.dump_model(req),
        )
        return GetDocAuthResponse.model_validate(data)

    def modify_doc_join_rule(
        self, request: ModifyDocJoinRuleRequest | dict[str, Any]
    ) -> ModifyDocJoinRuleResponse:
        """修改文档、表格或智能表格的加入规则。"""
        req = self._ensure_model(ModifyDocJoinRuleRequest, request)
        data = self._client.request_json(
            "POST",
            "/cgi-bin/wedoc/mod_doc_join_rule",
            json=self._client.dump_model(req),
        )
        return ModifyDocJoinRuleResponse.model_validate(data)

    def modify_doc_member(
        self, request: ModifyDocMemberRequest | dict[str, Any]
    ) -> ModifyDocMemberResponse:
        """增删文档成员，或修改成员权限。"""
        req = self._ensure_model(ModifyDocMemberRequest, request)
        data = self._client.request_json(
            "POST",
            "/cgi-bin/wedoc/mod_doc_member",
            json=self._client.dump_model(req),
        )
        return ModifyDocMemberResponse.model_validate(data)

    def modify_doc_safety_setting(
        self, request: ModifyDocSafetySettingRequest | dict[str, Any]
    ) -> ModifyDocSafetySettingResponse:
        """修改文档安全设置。

        企业微信官方接口路径为 `mod_doc_safty_setting`，这里保留公开方法名的正常拼写。
        """
        req = self._ensure_model(ModifyDocSafetySettingRequest, request)
        data = self._client.request_json(
            "POST",
            "/cgi-bin/wedoc/mod_doc_safty_setting",
            json=self._client.dump_model(req),
        )
        return ModifyDocSafetySettingResponse.model_validate(data)

    def get_sheet_priv(
        self, request: GetSheetPrivRequest | dict[str, Any]
    ) -> GetSheetPrivResponse:
        """查询智能表格子表内容权限。"""
        req = self._ensure_model(GetSheetPrivRequest, request)
        data = self._client.request_json(
            "POST",
            "/cgi-bin/wedoc/smartsheet/content_priv/get_sheet_priv",
            json=self._client.dump_model(req),
        )
        return GetSheetPrivResponse.model_validate(data)

    def update_sheet_priv(
        self, request: UpdateSheetPrivRequest | dict[str, Any]
    ) -> UpdateSheetPrivResponse:
        """设置全员权限或额外权限的子表权限详情。"""
        req = self._ensure_model(UpdateSheetPrivRequest, request)
        data = self._client.request_json(
            "POST",
            "/cgi-bin/wedoc/smartsheet/content_priv/update_sheet_priv",
            json=self._client.dump_model(req),
        )
        return UpdateSheetPrivResponse.model_validate(data)

    def create_sheet_priv_rule(
        self, request: CreateSheetPrivRuleRequest | dict[str, Any]
    ) -> CreateSheetPrivRuleResponse:
        """新增智能表格指定成员额外权限。"""
        req = self._ensure_model(CreateSheetPrivRuleRequest, request)
        data = self._client.request_json(
            "POST",
            "/cgi-bin/wedoc/smartsheet/content_priv/create_rule",
            json=self._client.dump_model(req),
        )
        return CreateSheetPrivRuleResponse.model_validate(data)

    def modify_sheet_priv_rule_member(
        self, request: ModifySheetPrivRuleMemberRequest | dict[str, Any]
    ) -> ModifySheetPrivRuleMemberResponse:
        """更新智能表格指定成员额外权限的生效成员。"""
        req = self._ensure_model(ModifySheetPrivRuleMemberRequest, request)
        data = self._client.request_json(
            "POST",
            "/cgi-bin/wedoc/smartsheet/content_priv/mod_rule_member",
            json=self._client.dump_model(req),
        )
        return ModifySheetPrivRuleMemberResponse.model_validate(data)

    def delete_sheet_priv_rules(
        self, request: DeleteSheetPrivRulesRequest | dict[str, Any]
    ) -> DeleteSheetPrivRulesResponse:
        """删除智能表格指定成员额外权限规则。"""
        req = self._ensure_model(DeleteSheetPrivRulesRequest, request)
        data = self._client.request_json(
            "POST",
            "/cgi-bin/wedoc/smartsheet/content_priv/delete_rule",
            json=self._client.dump_model(req),
        )
        return DeleteSheetPrivRulesResponse.model_validate(data)
