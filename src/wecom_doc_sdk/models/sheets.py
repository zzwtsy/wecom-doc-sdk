from __future__ import annotations

from typing import List, Optional

from pydantic import Field

from .common import WeComBaseModel, WeComBaseResponse
from .enums import SheetType


class AddSheetProperties(WeComBaseModel):
    """新增子表时的可选属性。"""

    # 新子表标题；不传时由企业微信使用默认标题。
    title: Optional[str] = Field(default=None, description="子表标题，可选")
    # 子表插入位置下标。
    index: Optional[int] = Field(default=None, description="子表插入位置下标")


class UpdateSheetProperties(WeComBaseModel):
    """更新子表时允许修改的属性。"""

    # 要更新的子表唯一标识。
    sheet_id: str = Field(description="待更新的子表 ID")
    # 子表的新标题；当前接口主要支持修改该字段。
    title: Optional[str] = Field(default=None, description="更新后的子表标题")


class SheetProperties(WeComBaseModel):
    """子表基础属性。

    常用于添加子表后的返回结果，包含企业微信生成的 `sheet_id`。
    """

    sheet_id: Optional[str] = Field(default=None, description="子表 ID")
    title: Optional[str] = Field(default=None, description="子表标题")
    index: Optional[int] = Field(default=None, description="子表顺序下标")


class SheetInfo(WeComBaseModel):
    """查询子表接口返回的子表信息。"""

    sheet_id: str = Field(description="子表 ID")
    title: str = Field(description="子表标题")
    # 子表是否在当前文档中可见。
    is_visible: bool = Field(description="子表是否可见")
    # 子表类型：智能表、仪表盘或说明页。
    type: SheetType = Field(description="子表类型")


class AddSheetRequest(WeComBaseModel):
    """添加子表请求体。"""

    docid: str = Field(description="文档 ID")
    properties: Optional[AddSheetProperties] = Field(
        default=None, description="新增子表属性"
    )


class AddSheetResponse(WeComBaseResponse):
    """添加子表响应体。"""

    properties: Optional[SheetProperties] = Field(
        default=None, description="新增后子表属性"
    )


class DeleteSheetRequest(WeComBaseModel):
    """删除子表请求体。"""

    docid: str = Field(description="文档 ID")
    sheet_id: str = Field(description="待删除子表 ID")


class DeleteSheetResponse(WeComBaseResponse):
    """删除子表响应体。"""

    pass


class UpdateSheetRequest(WeComBaseModel):
    """更新子表请求体。"""

    docid: str = Field(description="文档 ID")
    properties: UpdateSheetProperties = Field(description="更新子表属性")


class UpdateSheetResponse(WeComBaseResponse):
    """更新子表响应体。"""

    pass


class GetSheetRequest(WeComBaseModel):
    """查询子表请求体。"""

    docid: str = Field(description="文档 ID")
    # 仅查询指定子表时传入；为空时查询文档下全部子表。
    sheet_id: Optional[str] = Field(default=None, description="指定查询的子表 ID")
    # 为 `True` 时返回所有类型子表，包含仪表盘和说明页。
    need_all_type_sheet: Optional[bool] = Field(
        default=None, description="是否返回所有类型子表"
    )


class GetSheetResponse(WeComBaseResponse):
    """查询子表响应体。"""

    sheet_list: Optional[List[SheetInfo]] = Field(default=None, description="子表列表")
