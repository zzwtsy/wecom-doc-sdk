from __future__ import annotations

from typing import List, Optional

from .common import WeComBaseModel, WeComBaseResponse
from .enums import SheetType


class AddSheetProperties(WeComBaseModel):
    title: Optional[str] = None
    index: Optional[int] = None


class UpdateSheetProperties(WeComBaseModel):
    sheet_id: str
    title: Optional[str] = None


class SheetProperties(WeComBaseModel):
    sheet_id: Optional[str] = None
    title: Optional[str] = None
    index: Optional[int] = None


class SheetInfo(WeComBaseModel):
    sheet_id: str
    title: str
    is_visible: bool
    type: SheetType


class AddSheetRequest(WeComBaseModel):
    docid: str
    properties: Optional[AddSheetProperties] = None


class AddSheetResponse(WeComBaseResponse):
    properties: Optional[SheetProperties] = None


class DeleteSheetRequest(WeComBaseModel):
    docid: str
    sheet_id: str


class DeleteSheetResponse(WeComBaseResponse):
    pass


class UpdateSheetRequest(WeComBaseModel):
    docid: str
    properties: UpdateSheetProperties


class UpdateSheetResponse(WeComBaseResponse):
    pass


class GetSheetRequest(WeComBaseModel):
    docid: str
    sheet_id: Optional[str] = None
    need_all_type_sheet: Optional[bool] = None


class GetSheetResponse(WeComBaseResponse):
    sheet_list: Optional[List[SheetInfo]] = None
