from __future__ import annotations

from typing import Any

from ...client import WeComClient
from ...models.documents import CreateDocRequest
from ...models.enums import DocType
from ...models.fields import AddFieldsRequest
from ...models.sheets import AddSheetProperties, AddSheetRequest
from ..models import SheetCreateConfig, SheetTemplate, SmartSheetTemplate
from ..utils import load_template, print_json, require_value


def create_sheet_and_fields(
    client: WeComClient,
    *,
    docid: str,
    sheet_config: SheetCreateConfig,
    action_name: str,
) -> dict[str, Any]:
    """创建子表并按需补充字段。"""

    add_sheet_response = client.smartsheet.add_sheet(
        AddSheetRequest(
            docid=docid,
            properties=AddSheetProperties(
                title=sheet_config.title,
                index=sheet_config.index,
            ),
        )
    )
    sheet_id = require_value(
        (
            add_sheet_response.properties.sheet_id
            if add_sheet_response.properties
            else None
        ),
        "sheet_id",
        action_name,
    )

    result: dict[str, Any] = {
        "sheet_id": sheet_id,
        "title": sheet_config.title,
    }
    if sheet_config.index is not None:
        result["index"] = sheet_config.index

    if not sheet_config.fields:
        return result

    add_fields_response = client.smartsheet.add_fields(
        AddFieldsRequest(docid=docid, sheet_id=sheet_id, fields=sheet_config.fields)
    )
    if not add_fields_response.fields:
        from ..errors import CLIError

        raise CLIError("add_fields 返回缺少 fields")

    result["fields"] = [
        {
            "field_id": require_value(field.field_id, "field_id", "add_fields"),
            "field_title": require_value(
                field.field_title, "field_title", "add_fields"
            ),
            "field_type": field.field_type.value if field.field_type else None,
        }
        for field in add_fields_response.fields
    ]
    return result


def run_smartsheet_create(
    *,
    corp_id: str,
    corp_secret: str,
    template_path: str,
) -> dict[str, Any]:
    """按模板创建智能表格，并可选创建一个子表。"""

    template = load_template(SmartSheetTemplate, template_path)

    with WeComClient(corp_id, corp_secret) as client:
        doc_response = client.documents.create_doc(
            CreateDocRequest(
                spaceid=template.spaceid,
                fatherid=template.fatherid,
                doc_type=DocType.SMARTSHEET,
                doc_name=template.title,
                admin_users=template.admin_users,
            )
        )
        docid = require_value(doc_response.docid, "docid", "create_doc")
        result: dict[str, Any] = {
            "docid": docid,
            "title": template.title,
        }
        if doc_response.url:
            result["url"] = doc_response.url
        if template.spaceid:
            result["spaceid"] = template.spaceid
        if template.fatherid:
            result["fatherid"] = template.fatherid

        if template.sheet:
            result["sheet"] = create_sheet_and_fields(
                client,
                docid=docid,
                sheet_config=template.sheet,
                action_name="smartsheet create",
            )

    print_json(result)
    return result


def run_smartsheet_sheet_create(
    *,
    corp_id: str,
    corp_secret: str,
    template_path: str,
) -> dict[str, Any]:
    """在已有智能表格中创建子表。"""

    template = load_template(SheetTemplate, template_path)

    with WeComClient(corp_id, corp_secret) as client:
        sheet = create_sheet_and_fields(
            client,
            docid=template.docid,
            sheet_config=SheetCreateConfig(
                title=template.title,
                index=template.index,
                fields=template.fields,
            ),
            action_name="sheet create",
        )

    result = {"docid": template.docid, **sheet}
    print_json(result)
    return result
