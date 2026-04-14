from __future__ import annotations

from ...client import WeComClient
from ...models.enums import WedriveFileType
from ...models.uploads import CreateFileRequest, CreateSpaceRequest
from ..models import FolderTemplate, SpaceTemplate
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
