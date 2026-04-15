from __future__ import annotations

from ...client import WeComClient
from ...models.enums import WedriveFileType
from ...models.uploads import (
    AddSpaceAclRequest,
    CreateFileRequest,
    CreateSpaceAuthInfo,
    CreateSpaceRequest,
    GetSpaceInfoRequest,
)
from ..errors import CLIError
from ..models import FolderTemplate, SpaceAdminAddTemplate, SpaceTemplate
from ..utils import load_template, print_json, require_value


def run_space_create(
    *,
    corp_id: str,
    corp_secret: str,
    template_path: str,
) -> dict[str, object]:
    """按模板创建空间，并可选创建目录。"""

    template = load_template(SpaceTemplate, template_path)

    with WeComClient(corp_id, corp_secret) as client:
        space_response = client.uploads.create_space(
            CreateSpaceRequest(
                space_name=template.space_name,
                space_sub_type=template.space_sub_type,
                auth_info=template.auth_info,
            )
        )
        spaceid = require_value(space_response.spaceid, "spaceid", "create_space")

        result: dict[str, object] = {
            "spaceid": spaceid,
            "space_name": template.space_name,
        }
        if template.space_sub_type is not None:
            result["space_sub_type"] = template.space_sub_type

        if template.folder:
            folder_response = client.uploads.create_file(
                CreateFileRequest(
                    spaceid=spaceid,
                    fatherid=spaceid,
                    file_type=WedriveFileType.FOLDER,
                    file_name=template.folder.name,
                )
            )
            result["folder"] = {
                "fileid": require_value(
                    folder_response.fileid, "fileid", "create_file"
                ),
                "name": template.folder.name,
            }

    print_json(result)
    return result


def run_space_folder_create(
    *,
    corp_id: str,
    corp_secret: str,
    template_path: str,
) -> dict[str, object]:
    """在已有空间或目录下创建文件夹。"""

    template = load_template(FolderTemplate, template_path)

    with WeComClient(corp_id, corp_secret) as client:
        folder_response = client.uploads.create_file(
            CreateFileRequest(
                spaceid=template.spaceid,
                fatherid=template.fatherid,
                file_type=WedriveFileType.FOLDER,
                file_name=template.name,
            )
        )

    result: dict[str, object] = {
        "spaceid": template.spaceid,
        "fatherid": template.fatherid,
        "fileid": require_value(folder_response.fileid, "fileid", "create_file"),
        "name": template.name,
    }
    print_json(result)
    return result


def run_space_admin_add(
    *,
    corp_id: str,
    corp_secret: str,
    template_path: str,
) -> dict[str, object]:
    """给已有空间添加管理员。"""

    template = load_template(SpaceAdminAddTemplate, template_path)

    with WeComClient(corp_id, corp_secret) as client:
        space_info_response = client.uploads.get_space_info(
            GetSpaceInfoRequest(spaceid=template.spaceid)
        )
        auth_info = (
            space_info_response.space_info.auth_list.auth_info
            if space_info_response.space_info
            and space_info_response.space_info.auth_list
            and space_info_response.space_info.auth_list.auth_info
            else []
        )
        existing_admin_users = {
            auth.userid
            for auth in auth_info
            if auth.type == 1 and auth.auth == 7 and auth.userid
        }
        existing_admin_count = len(existing_admin_users)
        adding_admin_count = len(template.admin_users)
        if existing_admin_count + adding_admin_count > 3:
            raise CLIError(
                "space admin add 失败：应用空间管理员最多 3 人，"
                f"当前已有 {existing_admin_count} 人，本次新增 {adding_admin_count} 人"
            )

        client.uploads.add_space_acl(
            AddSpaceAclRequest(
                spaceid=template.spaceid,
                auth_info=[
                    CreateSpaceAuthInfo(type=1, userid=userid, auth=7)
                    for userid in template.admin_users
                ],
            )
        )

    result: dict[str, object] = {
        "spaceid": template.spaceid,
        "admin_users": template.admin_users,
        "existing_admin_count": existing_admin_count,
        "added_count": adding_admin_count,
    }
    print_json(result)
    return result
