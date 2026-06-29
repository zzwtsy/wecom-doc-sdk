from __future__ import annotations

from collections.abc import Callable

import pytest
from pydantic import ValidationError

from wecom_doc_sdk import WeComClient
from wecom_doc_sdk.apis import SmartSheetAPI
from wecom_doc_sdk.models.records import (
    AddRecord,
    CellAttachmentValue,
    CellTextFormat,
    CellTextValue,
    GetRecordsRequest,
    GetRecordsResponse,
    UpdateRecord,
)


def test_client_mounts_smartsheet_api(client: WeComClient) -> None:
    """客户端应默认挂载智能表 API。"""

    assert isinstance(client.smartsheet, SmartSheetAPI)


def test_get_records_response_allows_null_and_preserves_scalar_values() -> None:
    """查询记录响应应允许空单元格，并保留其他合法值类型。"""

    response = GetRecordsResponse.model_validate(
        {
            "errcode": 0,
            "errmsg": "ok",
            "records": [
                {
                    "record_id": "r1",
                    "values": {
                        "空字段": None,
                        "复选框字段": True,
                        "数字字段": 123,
                        "进度字段": 12.5,
                        "电话字段": "13800138000",
                        "关联字段": ["rec-1", "rec-2"],
                    },
                }
            ],
        }
    )

    assert response.records is not None
    values = response.records[0].values
    assert values["空字段"] is None
    assert values["复选框字段"] is True
    assert values["数字字段"] == 123
    assert values["进度字段"] == pytest.approx(12.5)
    assert values["电话字段"] == "13800138000"
    assert values["关联字段"] == ["rec-1", "rec-2"]


def test_get_records_response_parses_attachment_value_without_falling_back() -> None:
    """附件单元格应解析为文件对象，而不是误判成图片对象。"""

    response = GetRecordsResponse.model_validate(
        {
            "errcode": 0,
            "errmsg": "ok",
            "records": [
                {
                    "record_id": "r1",
                    "values": {
                        "附件字段": [
                            {
                                "doc_type": 2,
                                "file_ext": "SMARTSHEET",
                                "file_id": "FILEID",
                                "file_type": "70",
                                "file_url": "https://doc.weixin.qq.com/smartsheet/xxx",
                                "name": "智能表格",
                                "size": 3267,
                            }
                        ]
                    },
                }
            ],
        }
    )

    assert response.records is not None
    attachment_value = response.records[0].values["附件字段"]
    assert isinstance(attachment_value, list)
    assert len(attachment_value) == 1
    assert isinstance(attachment_value[0], CellAttachmentValue)
    assert attachment_value[0].doc_type == 2
    assert attachment_value[0].file_id == "FILEID"


def test_get_records_response_rejects_unknown_attachment_keys() -> None:
    """附件对象包含未知字段时应失败，避免联合类型误判。"""

    with pytest.raises(ValidationError):
        GetRecordsResponse.model_validate(
            {
                "errcode": 0,
                "errmsg": "ok",
                "records": [
                    {
                        "record_id": "r1",
                        "values": {
                            "附件字段": [
                                {
                                    "doc_type": 2,
                                    "file_id": "FILEID",
                                    "file_type": "70",
                                    "name": "智能表格",
                                    "unexpected_field": "future-value",
                                }
                            ]
                        },
                    }
                ],
            }
        )


def test_get_records_response_parses_text_segments_with_format() -> None:
    """带富文本样式的文本段应被解析为 `CellTextValue`/`CellUrlValue`，而非整格失败。

    复刻线上“问题描述”单元格的真实结构：普通文本段与带 `format`/`link` 的
    `type=url` 段混合。`format` 富文本样式此前会触发 `extra_forbidden`，
    进而在联合类型逐分支兜底中放大成几十条校验错误。
    """

    response = GetRecordsResponse.model_validate(
        {
            "errcode": 0,
            "errmsg": "ok",
            "records": [
                {
                    "record_id": "r1",
                    "values": {
                        "问题描述": [
                            {
                                "text": "订单问题：—6天*1.5=9美金\n",
                                "type": "text",
                            },
                            {
                                "text": "今日中行汇率6.82，折合人民币61.38元\n",
                                "type": "text",
                            },
                            {
                                "text": "对公支付宝-账号：",
                                "type": "text",
                            },
                            {
                                "format": {
                                    "font_color": "rgb(38, 126, 240)",
                                    "underline": True,
                                },
                                "link": "mailto:test@test.com",
                                "text": "test@test.com",
                                "type": "url",
                            },
                            {
                                "text": "付款备注订单号+费用…",
                                "type": "text",
                            },
                        ]
                    },
                }
            ],
        }
    )

    assert response.records is not None
    segments = response.records[0].values["问题描述"]
    assert isinstance(segments, list)
    assert len(segments) == 5

    assert isinstance(segments[0], CellTextValue)
    assert segments[0].type.value == "text"
    assert segments[0].format is None

    # `CellTextValue` 在联合类型中排首位且同时接受 `type=text`/`type=url`，
    # 因此带 `link` 的 url 段也解析为 `CellTextValue`，而非独立的 `CellUrlValue`。
    # 真实数据中 `link` 为带 `mailto:` 前缀的完整 URL，`text` 为展示用的纯邮箱。
    url_segment = segments[3]
    assert isinstance(url_segment, CellTextValue)
    assert url_segment.type.value == "url"
    assert url_segment.text == "test@test.com"
    assert url_segment.link == "mailto:test@test.com"
    assert isinstance(url_segment.format, CellTextFormat)
    assert url_segment.format.font_color == "rgb(38, 126, 240)"
    assert url_segment.format.underline is True

    assert isinstance(segments[4], CellTextValue)
    assert segments[4].text == "付款备注订单号+费用…"


def test_add_record_rejects_none_values() -> None:
    """新增记录仍不应接受 `None` 作为写入值。"""

    with pytest.raises(ValidationError):
        AddRecord.model_validate({"values": {"空字段": None}})


def test_update_record_rejects_none_values() -> None:
    """更新记录仍不应接受 `None` 作为写入值。"""

    with pytest.raises(ValidationError):
        UpdateRecord.model_validate({"record_id": "r1", "values": {"空字段": None}})


def test_get_records_api_parses_query_values_and_uses_official_path(
    client: WeComClient,
    bind_request_json: Callable[[dict[str, object]], dict[str, object]],
) -> None:
    """API 层应命中正确路径，并透传查询侧可空 values。"""

    captured = bind_request_json(
        {
            "errcode": 0,
            "errmsg": "ok",
            "records": [
                {
                    "record_id": "r1",
                    "values": {
                        "空字段": None,
                        "附件字段": [
                            {
                                "doc_type": 2,
                                "file_type": "70",
                                "name": "智能表格",
                            }
                        ],
                    },
                }
            ],
        },
    )

    response = client.smartsheet.get_records(
        GetRecordsRequest(docid="DOCID", sheet_id="SHEETID")
    )

    assert captured["method"] == "POST"
    assert captured["path"] == "/cgi-bin/wedoc/smartsheet/get_records"
    assert captured["json"] == {"docid": "DOCID", "sheet_id": "SHEETID"}
    assert response.records is not None
    assert response.records[0].values["空字段"] is None
    attachment_value = response.records[0].values["附件字段"]
    assert isinstance(attachment_value, list)
    assert isinstance(attachment_value[0], CellAttachmentValue)
