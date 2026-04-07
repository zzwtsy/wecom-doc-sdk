from __future__ import annotations

from typing import List, Optional

from pydantic import Field

from .common import WeComBaseModel, WeComBaseResponse
from .enums import (
    CoAuthType,
    DocJoinRuleAuth,
    DocMemberAuth,
    DocMemberType,
    DocWatermarkMarginType,
    FieldType,
    SheetPrivFieldRangeType,
    SheetPrivRecordOperType,
    SheetPrivRecordOtherPriv,
    SheetPrivRecordRangeType,
    SheetPrivRuleType,
    SheetPrivType,
)


class DocAccessRule(WeComBaseModel):
    """文档查看规则。"""

    # 是否允许企业内成员主动浏览文档。
    enable_corp_internal: Optional[bool] = Field(
        default=None, description="是否允许企业内浏览"
    )
    # 企业内成员主动浏览后获得的权限类型。
    corp_internal_auth: Optional[DocJoinRuleAuth] = Field(
        default=None, description="企业内浏览后的默认权限"
    )
    # 是否允许企业外成员主动浏览文档。
    enable_corp_external: Optional[bool] = Field(
        default=None, description="是否允许企业外浏览"
    )
    # 企业外成员主动浏览后获得的权限类型。
    corp_external_auth: Optional[DocJoinRuleAuth] = Field(
        default=None, description="企业外浏览后的默认权限"
    )
    # 企业内成员加入文档时是否必须由管理员审批。
    corp_internal_approve_only_by_admin: Optional[bool] = Field(
        default=None, description="企业内加入是否需管理员审批"
    )
    # 企业外成员加入文档时是否必须由管理员审批。
    corp_external_approve_only_by_admin: Optional[bool] = Field(
        default=None, description="企业外加入是否需管理员审批"
    )
    # 是否禁止文档分享到企业外。
    ban_share_external: Optional[bool] = Field(
        default=None, description="是否禁止外部分享"
    )


class DocWatermark(WeComBaseModel):
    """文档水印配置。"""

    margin_type: Optional[DocWatermarkMarginType] = Field(
        default=None, description="水印边距样式"
    )
    show_visitor_name: Optional[bool] = Field(
        default=None, description="是否显示访问者名称"
    )
    show_text: Optional[bool] = Field(default=None, description="是否显示自定义文字")
    text: Optional[str] = Field(default=None, description="水印自定义文本")


class DocSecureSetting(WeComBaseModel):
    """文档安全设置。"""

    # 只读成员是否允许复制、导出或打印。
    enable_readonly_copy: Optional[bool] = Field(
        default=None, description="只读成员是否可复制导出"
    )
    # 只读成员是否允许发表评论。
    enable_readonly_comment: Optional[bool] = Field(
        default=None, description="只读成员是否可评论"
    )
    # 文档水印设置。
    watermark: Optional[DocWatermark] = Field(default=None, description="水印配置")


class DocMember(WeComBaseModel):
    """文档成员及其权限。"""

    # 文档成员类型，目前接口文档仅支持 1: 用户。
    type: DocMemberType = Field(description="成员类型")
    userid: Optional[str] = Field(default=None, description="企业成员 userid")
    tmp_external_userid: Optional[str] = Field(
        default=None, description="外部联系人临时 ID"
    )
    # 文档成员权限：1 只读，2 读写，7 管理员。
    auth: Optional[DocMemberAuth] = Field(default=None, description="成员权限")


class DocMemberTarget(WeComBaseModel):
    """删除文档成员时的目标对象。"""

    type: DocMemberType = Field(description="成员类型")
    userid: Optional[str] = Field(default=None, description="企业成员 userid")
    tmp_external_userid: Optional[str] = Field(
        default=None, description="外部联系人临时 ID"
    )


class CoAuthDepartment(WeComBaseModel):
    """文档查看权限的特定部门配置。"""

    # 特定部门列表，目前接口文档仅支持 2: 部门。
    type: CoAuthType = Field(description="共享对象类型")
    departmentid: int = Field(description="部门 ID")
    # 权限类型：1 只读，2 读写。
    auth: DocJoinRuleAuth = Field(description="部门默认权限")


class GetDocAuthRequest(WeComBaseModel):
    """获取文档权限信息请求体。"""

    docid: str


class GetDocAuthResponse(WeComBaseResponse):
    """获取文档权限信息响应体。"""

    access_rule: Optional[DocAccessRule] = None
    secure_setting: Optional[DocSecureSetting] = None
    doc_member_list: Optional[List[DocMember]] = None
    co_auth_list: Optional[List[CoAuthDepartment]] = None


class ModifyDocJoinRuleRequest(WeComBaseModel):
    """修改文档加入规则请求体。"""

    docid: str
    enable_corp_internal: Optional[bool] = None
    corp_internal_auth: Optional[DocJoinRuleAuth] = None
    enable_corp_external: Optional[bool] = None
    corp_external_auth: Optional[DocJoinRuleAuth] = None
    corp_internal_approve_only_by_admin: Optional[bool] = None
    corp_external_approve_only_by_admin: Optional[bool] = None
    ban_share_external: Optional[bool] = None
    update_co_auth_list: Optional[bool] = None
    co_auth_list: Optional[List[CoAuthDepartment]] = None


class ModifyDocJoinRuleResponse(WeComBaseResponse):
    """修改文档加入规则响应体。"""

    pass


class ModifyDocMemberRequest(WeComBaseModel):
    """修改文档成员与权限请求体。"""

    docid: str
    update_file_member_list: Optional[List[DocMember]] = None
    del_file_member_list: Optional[List[DocMemberTarget]] = None


class ModifyDocMemberResponse(WeComBaseResponse):
    """修改文档成员与权限响应体。"""

    pass


class ModifyDocSafetySettingRequest(WeComBaseModel):
    """修改文档安全设置请求体。"""

    docid: str
    enable_readonly_copy: Optional[bool] = None
    enable_readonly_comment: Optional[bool] = None
    watermark: Optional[DocWatermark] = None


class ModifyDocSafetySettingResponse(WeComBaseResponse):
    """修改文档安全设置响应体。"""

    pass


class SheetPrivMemberRange(WeComBaseModel):
    """智能表格权限规则的成员范围。"""

    userid_list: Optional[List[str]] = None


class SheetPrivFieldRule(WeComBaseModel):
    """字段级权限规则。"""

    field_id: str
    field_type: Optional[FieldType] = None
    can_edit: Optional[bool] = None
    can_insert: Optional[bool] = None
    can_view: Optional[bool] = None


class SheetPrivFieldDefaultRule(WeComBaseModel):
    """字段默认权限规则。"""

    can_edit: Optional[bool] = None
    can_insert: Optional[bool] = None
    can_view: Optional[bool] = None


class SheetPrivFieldPriv(WeComBaseModel):
    """字段范围权限配置。"""

    field_range_type: SheetPrivFieldRangeType
    field_rule_list: Optional[List[SheetPrivFieldRule]] = None
    field_default_rule: Optional[SheetPrivFieldDefaultRule] = None


class SheetPrivRecordRule(WeComBaseModel):
    """记录范围筛选条件。"""

    field_id: str
    field_type: Optional[FieldType] = None
    oper_type: SheetPrivRecordOperType
    value: Optional[List[str]] = None


class SheetPrivRecordPriv(WeComBaseModel):
    """记录级权限配置。"""

    record_range_type: SheetPrivRecordRangeType
    record_rule_list: Optional[List[SheetPrivRecordRule]] = None
    other_priv: Optional[SheetPrivRecordOtherPriv] = None


class SheetPrivItem(WeComBaseModel):
    """单个子表权限配置。"""

    sheet_id: str
    priv: SheetPrivType
    can_insert_record: Optional[bool] = None
    can_delete_record: Optional[bool] = None
    can_create_modify_delete_view: Optional[bool] = None
    field_priv: Optional[SheetPrivFieldPriv] = None
    record_priv: Optional[SheetPrivRecordPriv] = None
    clear: Optional[bool] = None


class SheetPrivRule(WeComBaseModel):
    """智能表格内容权限规则。"""

    rule_id: Optional[int] = None
    type: SheetPrivRuleType
    name: Optional[str] = None
    priv_list: Optional[List[SheetPrivItem]] = None


class GetSheetPrivRequest(WeComBaseModel):
    """查询智能表格子表权限请求体。"""

    docid: str
    type: SheetPrivRuleType
    rule_id_list: Optional[List[int]] = None


class GetSheetPrivResponse(WeComBaseResponse):
    """查询智能表格子表权限响应体。"""

    rule_list: Optional[List[SheetPrivRule]] = None


class UpdateSheetPrivRequest(WeComBaseModel):
    """更新智能表格子表权限请求体。"""

    docid: str
    type: SheetPrivRuleType
    rule_id: Optional[int] = None
    name: Optional[str] = None
    priv_list: Optional[List[SheetPrivItem]] = None


class UpdateSheetPrivResponse(WeComBaseResponse):
    """更新智能表格子表权限响应体。"""

    pass


class CreateSheetPrivRuleRequest(WeComBaseModel):
    """新增智能表格指定成员额外权限请求体。"""

    docid: str
    name: str


class CreateSheetPrivRuleResponse(WeComBaseResponse):
    """新增智能表格指定成员额外权限响应体。"""

    rule_id: Optional[int] = None


class ModifySheetPrivRuleMemberRequest(WeComBaseModel):
    """更新智能表格指定成员额外权限请求体。"""

    docid: str
    rule_id: int
    add_member_range: Optional[SheetPrivMemberRange] = None
    del_member_range: Optional[SheetPrivMemberRange] = None


class ModifySheetPrivRuleMemberResponse(WeComBaseResponse):
    """更新智能表格指定成员额外权限响应体。"""

    pass


class DeleteSheetPrivRulesRequest(WeComBaseModel):
    """删除智能表格指定成员额外权限请求体。"""

    docid: str
    rule_id_list: List[int]


class DeleteSheetPrivRulesResponse(WeComBaseResponse):
    """删除智能表格指定成员额外权限响应体。"""

    pass
