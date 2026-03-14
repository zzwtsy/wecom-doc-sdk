from __future__ import annotations

from typing import Dict, List, Optional, Union

from .common import WeComBaseModel, WeComBaseResponse
from .enums import CellValueKeyType
from .fields import Option
from .views import FilterSpec


class CellTextValue(WeComBaseModel):
    """文本/链接单元格值。"""

    type: str
    text: Optional[str] = None
    link: Optional[str] = None


class CellImageValue(WeComBaseModel):
    id: Optional[str] = None
    title: Optional[str] = None
    image_url: Optional[str] = None
    width: Optional[int] = None
    height: Optional[int] = None


class CellAttachmentValue(WeComBaseModel):
    name: Optional[str] = None
    size: Optional[int] = None
    file_ext: Optional[str] = None
    file_id: Optional[str] = None
    file_url: Optional[str] = None
    file_type: Optional[str] = None
    doc_type: Optional[str] = None


class CellUserValue(WeComBaseModel):
    user_id: Optional[str] = None
    tmp_external_userid: Optional[str] = None
    agentid: Optional[int] = None
    id_type: Optional[int] = None


class CellUrlValue(WeComBaseModel):
    type: str = "url"
    text: Optional[str] = None
    link: Optional[str] = None


class CellLocationValue(WeComBaseModel):
    source_type: Optional[int] = None
    id: Optional[str] = None
    latitude: Optional[str] = None
    longitude: Optional[str] = None
    title: Optional[str] = None


class CellAutoNumberValue(WeComBaseModel):
    seq: Optional[str] = None
    text: Optional[str] = None


CellValue = Union[
    List[CellTextValue],
    List[CellImageValue],
    List[CellAttachmentValue],
    List[CellUserValue],
    List[CellUrlValue],
    List[CellLocationValue],
    List[CellAutoNumberValue],
    List[Option],
    List[str],
    bool,
    int,
    float,
    str,
]

RecordValues = Dict[str, CellValue]


class AddRecord(WeComBaseModel):
    values: RecordValues


class UpdateRecord(WeComBaseModel):
    record_id: str
    values: RecordValues


class CommonRecord(WeComBaseModel):
    record_id: str
    values: RecordValues


class Record(CommonRecord):
    create_time: Optional[str] = None
    update_time: Optional[str] = None
    creator_name: Optional[str] = None
    updater_name: Optional[str] = None


class Sort(WeComBaseModel):
    field_title: str
    desc: Optional[bool] = None


class AddRecordsRequest(WeComBaseModel):
    docid: str
    sheet_id: str
    key_type: Optional[CellValueKeyType] = None
    records: List[AddRecord]


class AddRecordsResponse(WeComBaseResponse):
    records: Optional[List[CommonRecord]] = None


class UpdateRecordsRequest(WeComBaseModel):
    docid: str
    sheet_id: str
    key_type: Optional[CellValueKeyType] = None
    records: List[UpdateRecord]


class UpdateRecordsResponse(WeComBaseResponse):
    records: Optional[List[CommonRecord]] = None


class DeleteRecordsRequest(WeComBaseModel):
    docid: str
    sheet_id: str
    record_ids: List[str]


class DeleteRecordsResponse(WeComBaseResponse):
    pass


class GetRecordsRequest(WeComBaseModel):
    docid: str
    sheet_id: str
    view_id: Optional[str] = None
    record_ids: Optional[List[str]] = None
    key_type: Optional[CellValueKeyType] = None
    field_titles: Optional[List[str]] = None
    field_ids: Optional[List[str]] = None
    sort: Optional[List[Sort]] = None
    offset: Optional[int] = None
    limit: Optional[int] = None
    ver: Optional[int] = None
    filter_spec: Optional[FilterSpec] = None


class GetRecordsResponse(WeComBaseResponse):
    total: Optional[int] = None
    has_more: Optional[bool] = None
    next: Optional[int] = None
    records: Optional[List[Record]] = None
    ver: Optional[int] = None
