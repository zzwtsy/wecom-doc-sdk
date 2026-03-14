from __future__ import annotations

from typing import List, Optional

from .common import WeComBaseModel, WeComBaseResponse
from .enums import SheetType


class AddSheetProperties(WeComBaseModel):
    """新增子表时的可选属性。"""

    # 新子表标题；不传时由企业微信使用默认标题。
    title: Optional[str] = None
    # 子表插入位置下标。
    index: Optional[int] = None


class UpdateSheetProperties(WeComBaseModel):
    """更新子表时允许修改的属性。"""

    # 要更新的子表唯一标识。
    sheet_id: str
    # 子表的新标题；当前接口主要支持修改该字段。
    title: Optional[str] = None


class SheetProperties(WeComBaseModel):
    """子表基础属性。

    常用于添加子表后的返回结果，包含企业微信生成的 `sheet_id`。
    """

    sheet_id: Optional[str] = None
    title: Optional[str] = None
    index: Optional[int] = None


class SheetInfo(WeComBaseModel):
    """查询子表接口返回的子表信息。"""

    sheet_id: str
    title: str
    # 子表是否在当前文档中可见。
    is_visible: bool
    # 子表类型：智能表、仪表盘或说明页。
    type: SheetType


class AddSheetRequest(WeComBaseModel):
    """添加子表请求体。"""

    docid: str
    properties: Optional[AddSheetProperties] = None


class AddSheetResponse(WeComBaseResponse):
    """添加子表响应体。"""

    properties: Optional[SheetProperties] = None


class DeleteSheetRequest(WeComBaseModel):
    """删除子表请求体。"""

    docid: str
    sheet_id: str


class DeleteSheetResponse(WeComBaseResponse):
    """删除子表响应体。"""

    pass


class UpdateSheetRequest(WeComBaseModel):
    """更新子表请求体。"""

    docid: str
    properties: UpdateSheetProperties


class UpdateSheetResponse(WeComBaseResponse):
    """更新子表响应体。"""

    pass


class GetSheetRequest(WeComBaseModel):
    """查询子表请求体。"""

    docid: str
    # 仅查询指定子表时传入；为空时查询文档下全部子表。
    sheet_id: Optional[str] = None
    # 为 `True` 时返回所有类型子表，包含仪表盘和说明页。
    need_all_type_sheet: Optional[bool] = None


class GetSheetResponse(WeComBaseResponse):
    """查询子表响应体。"""

    sheet_list: Optional[List[SheetInfo]] = None
