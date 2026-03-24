from __future__ import annotations

from typing import Any, Type, TypeVar

from pydantic import BaseModel

from ..client import WeComClient
from ..models.permissions import (
    GetDocAuthRequest,
    GetDocAuthResponse,
    ModifyDocJoinRuleRequest,
    ModifyDocJoinRuleResponse,
    ModifyDocMemberRequest,
    ModifyDocMemberResponse,
    ModifyDocSafetySettingRequest,
    ModifyDocSafetySettingResponse,
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
