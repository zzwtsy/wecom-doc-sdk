from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from ...client import WeComClient
from ...models.documents import CreateDocRequest
from ...models.enums import DocType, WedriveFileType
from ...models.uploads import CreateFileRequest, CreateSpaceRequest
from ..models import (
    ScaffoldTemplate,
    ScaffoldWedriveCreateConfig,
    SheetCreateConfig,
)
from ..utils import (
    build_success_payload,
    load_template,
    print_json,
    require_auth_args,
    require_value,
    resolve_manifest_path,
)
from .smartsheet import create_sheet_and_fields


def build_dry_run_summary(
    template: ScaffoldTemplate,
    template_path: Path,
    manifest_path: Path,
) -> dict[str, Any]:
    """生成 dry-run 输出。"""

    actions: list[dict[str, Any]] = []
    if isinstance(template.wedrive, ScaffoldWedriveCreateConfig):
        actions.append(
            {
                "step": "create_space",
                "space_name": template.wedrive.space_name,
                "space_sub_type": template.wedrive.space_sub_type,
                "auth_info_count": len(template.wedrive.auth_info or []),
            }
        )
        if template.wedrive.folder_name:
            actions.append(
                {
                    "step": "create_folder",
                    "folder_name": template.wedrive.folder_name,
                }
            )
    else:
        actions.append(
            {
                "step": "use_existing_wedrive",
                "spaceid": template.wedrive.spaceid,
                "fatherid": template.wedrive.fatherid,
            }
        )

    actions.append(
        {
            "step": "create_doc",
            "title": template.doc.title,
            "doc_type": DocType.SMARTSHEET.value,
        }
    )
    for index, sheet in enumerate(template.sheets):
        actions.append(
            {"step": "add_sheet", "index": index, "title": sheet.title}
        )
        actions.append(
            {
                "step": "add_fields",
                "sheet_title": sheet.title,
                "field_titles": [field.field_title for field in sheet.fields],
            }
        )

    return {
        "status": "success",
        "action": "scaffold",
        "mode": "dry-run",
        "path": str(manifest_path.resolve()),
        "template_path": str(template_path.resolve()),
        "manifest_path": str(manifest_path.resolve()),
        "actions": actions,
    }


def run_scaffold(
    *,
    corp_id: str | None,
    corp_secret: str | None,
    template_path: Path,
    output_path: Path | None = None,
    dry_run: bool = False,
) -> Path:
    """执行脚手架命令并返回 manifest 路径。"""

    template = load_template(ScaffoldTemplate, template_path)
    manifest_path = resolve_manifest_path(template_path, output_path)

    if dry_run:
        print_json(build_dry_run_summary(template, template_path, manifest_path))
        return manifest_path

    corp_id, corp_secret = require_auth_args(
        corp_id=corp_id,
        corp_secret=corp_secret,
        action_name="scaffold",
    )

    with WeComClient(corp_id, corp_secret) as client:
        if isinstance(template.wedrive, ScaffoldWedriveCreateConfig):
            create_space_response = client.uploads.create_space(
                CreateSpaceRequest(
                    space_name=template.wedrive.space_name,
                    space_sub_type=template.wedrive.space_sub_type,
                    auth_info=template.wedrive.auth_info,
                )
            )
            spaceid = require_value(
                create_space_response.spaceid, "spaceid", "create_space"
            )
            fatherid = spaceid
            if template.wedrive.folder_name:
                create_folder_response = client.uploads.create_file(
                    CreateFileRequest(
                        spaceid=spaceid,
                        fatherid=spaceid,
                        file_type=WedriveFileType.FOLDER,
                        file_name=template.wedrive.folder_name,
                    )
                )
                fatherid = require_value(
                    create_folder_response.fileid, "fileid", "create_file"
                )
        else:
            spaceid = template.wedrive.spaceid
            fatherid = template.wedrive.fatherid

        create_doc_response = client.documents.create_doc(
            CreateDocRequest(
                spaceid=spaceid,
                fatherid=fatherid,
                doc_type=DocType.SMARTSHEET,
                doc_name=template.doc.title,
            )
        )
        docid = require_value(create_doc_response.docid, "docid", "create_doc")

        manifest_sheets: list[dict[str, Any]] = []
        for index, sheet in enumerate(template.sheets):
            sheet_result = create_sheet_and_fields(
                client,
                docid=docid,
                sheet_config=SheetCreateConfig(
                    title=sheet.title,
                    index=index,
                    fields=sheet.fields,
                ),
                action_name="scaffold add_sheet",
            )
            manifest_fields = {
                field["field_title"]: {
                    "field_id": field["field_id"],
                    "field_type": field["field_type"],
                }
                for field in sheet_result.get("fields", [])
            }
            manifest_sheets.append(
                {
                    "title": sheet.title,
                    "sheet_id": sheet_result["sheet_id"],
                    "fields": manifest_fields,
                }
            )

    manifest = {
        "template_path": str(template_path.resolve()),
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "wedrive": {"spaceid": spaceid, "fatherid": fatherid},
        "doc": {"docid": docid, "title": template.doc.title},
        "sheets": manifest_sheets,
    }

    manifest_path.parent.mkdir(parents=True, exist_ok=True)
    manifest_path.write_text(
        json.dumps(manifest, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )
    print_json(
        build_success_payload(
            "scaffold",
            path=str(manifest_path.resolve()),
            manifest_path=str(manifest_path.resolve()),
            template_path=str(template_path.resolve()),
            spaceid=spaceid,
            fatherid=fatherid,
            docid=docid,
            sheet_count=len(manifest_sheets),
        )
    )
    return manifest_path
