from __future__ import annotations

from ...client import WeComClient
from ...models.enums import DocMemberAuth, DocMemberType
from ...models.permissions import DocMember, ModifyDocMemberRequest
from ..models import DocAdminAddTemplate
from ..utils import load_template, print_json


def run_doc_admin_add(
    *,
    corp_id: str,
    corp_secret: str,
    template_path: str,
) -> dict[str, object]:
    """给已有文档添加管理员。"""

    template = load_template(DocAdminAddTemplate, template_path)

    with WeComClient(corp_id, corp_secret) as client:
        client.permissions.modify_doc_member(
            ModifyDocMemberRequest(
                docid=template.docid,
                update_file_member_list=[
                    DocMember(
                        type=DocMemberType.USER,
                        userid=userid,
                        auth=DocMemberAuth.ADMIN,
                    )
                    for userid in template.admin_users
                ],
            )
        )

    result: dict[str, object] = {
        "docid": template.docid,
        "admin_users": template.admin_users,
        "added_count": len(template.admin_users),
    }
    print_json(result)
    return result
