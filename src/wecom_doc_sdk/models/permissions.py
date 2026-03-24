from __future__ import annotations

from typing import List, Optional

from .common import WeComBaseModel, WeComBaseResponse


class DocAccessRule(WeComBaseModel):
    """文档查看规则。"""

    # 是否允许企业内成员主动浏览文档。
    enable_corp_internal: Optional[bool] = None
    # 企业内成员主动浏览后获得的权限类型。
    corp_internal_auth: Optional[int] = None
    # 是否允许企业外成员主动浏览文档。
    enable_corp_external: Optional[bool] = None
    # 企业外成员主动浏览后获得的权限类型。
    corp_external_auth: Optional[int] = None
    # 企业内成员加入文档时是否必须由管理员审批。
    corp_internal_approve_only_by_admin: Optional[bool] = None
    # 企业外成员加入文档时是否必须由管理员审批。
    corp_external_approve_only_by_admin: Optional[bool] = None
    # 是否禁止文档分享到企业外。
    ban_share_external: Optional[bool] = None


class DocWatermark(WeComBaseModel):
    """文档水印配置。"""

    margin_type: Optional[int] = None
    show_visitor_name: Optional[bool] = None
    show_text: Optional[bool] = None
    text: Optional[str] = None


class DocSecureSetting(WeComBaseModel):
    """文档安全设置。"""

    # 只读成员是否允许复制、导出或打印。
    enable_readonly_copy: Optional[bool] = None
    # 只读成员是否允许发表评论。
    enable_readonly_comment: Optional[bool] = None
    # 文档水印设置。
    watermark: Optional[DocWatermark] = None


class DocMember(WeComBaseModel):
    """文档成员及其权限。"""

    # 文档成员类型，目前接口文档仅支持 1: 用户。
    type: int
    userid: Optional[str] = None
    tmp_external_userid: Optional[str] = None
    # 文档成员权限：1 只读，2 读写，7 管理员。
    auth: Optional[int] = None


class DocMemberTarget(WeComBaseModel):
    """删除文档成员时的目标对象。"""

    type: int
    userid: Optional[str] = None
    tmp_external_userid: Optional[str] = None


class CoAuthDepartment(WeComBaseModel):
    """文档查看权限的特定部门配置。"""

    # 特定部门列表，目前接口文档仅支持 2: 部门。
    type: int
    departmentid: int
    # 权限类型：1 只读，2 读写。
    auth: int


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
    corp_internal_auth: Optional[int] = None
    enable_corp_external: Optional[bool] = None
    corp_external_auth: Optional[int] = None
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
