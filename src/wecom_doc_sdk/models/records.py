from __future__ import annotations

from typing import Dict, List, Optional, Union

from pydantic import ConfigDict, Field

from .common import WeComBaseModel, WeComBaseResponse
from .enums import (
    CellAttachmentDocType,
    CellLocationSourceType,
    CellTextType,
    CellUserIdType,
    CellValueKeyType,
)
from .fields import Option
from .views import FilterSpec


class CellTextValue(WeComBaseModel):
    """文本或文本链接单元格值。"""

    # 记录单元格的对象结构需要可区分，避免被错误解析成其他类型的单元格值。
    model_config = ConfigDict(extra="forbid")

    # `text` 表示普通文本，`url` 表示带跳转链接的文本。
    type: CellTextType = Field(description="文本值类型")
    text: Optional[str] = Field(default=None, description="文本内容")
    # 当 `type` 为 `url` 时表示跳转地址。
    link: Optional[str] = Field(default=None, description="链接地址（type=url 时有效）")


class CellImageValue(WeComBaseModel):
    """图片单元格值。"""

    # 图片、文件等对象字段彼此有重叠风险，这里显式禁止额外字段以提高判别准确性。
    model_config = ConfigDict(extra="forbid")

    # 添加记录时可自定义图片 ID；查询时则为接口返回的图片标识。
    id: Optional[str] = Field(default=None, description="图片 ID")
    title: Optional[str] = Field(default=None, description="图片标题")
    image_url: Optional[str] = Field(default=None, description="图片 URL")
    width: Optional[int] = Field(default=None, description="图片宽度")
    height: Optional[int] = Field(default=None, description="图片高度")


class CellAttachmentValue(WeComBaseModel):
    """文件单元格值。"""

    # 查询响应里的文件对象字段较固定，禁止额外字段可避免误判为图片等类型。
    model_config = ConfigDict(extra="forbid")

    name: Optional[str] = Field(default=None, description="附件名称")
    size: Optional[int] = Field(default=None, description="附件大小（字节）")
    file_ext: Optional[str] = Field(default=None, description="附件扩展名")
    file_id: Optional[str] = Field(default=None, description="附件 ID")
    file_url: Optional[str] = Field(default=None, description="附件 URL")
    # 文档、表格、智能表等文件类型编码会通过该字段返回。
    file_type: Optional[str] = Field(default=None, description="附件文件类型编码")
    # `1` 表示文件夹，`2` 表示文件；按文档示例兼容数值语义。
    doc_type: Optional[CellAttachmentDocType] = Field(
        default=None, description="附件对象类型"
    )


class CellUserValue(WeComBaseModel):
    """人员单元格值。"""

    # 人员单元格返回结构固定，禁止额外字段可减少联合类型误判。
    model_config = ConfigDict(extra="forbid")

    user_id: Optional[str] = Field(default=None, description="成员 user_id")
    # 外部联系人的临时 ID；跨智能表不稳定，必要时需再做转换。
    tmp_external_userid: Optional[str] = Field(
        default=None, description="外部联系人临时 ID"
    )
    # 当值来源于应用时会返回应用 ID。
    agentid: Optional[int] = Field(default=None, description="应用 agentid")
    # 标识本条值是成员、外部联系人、应用还是系统自动写入。
    id_type: Optional[CellUserIdType] = Field(
        default=None, description="人员值来源类型"
    )


class CellUrlValue(WeComBaseModel):
    """超链接单元格值。"""

    # 链接对象结构简单且固定，禁止额外字段可避免误入其他对象分支。
    model_config = ConfigDict(extra="forbid")

    # 当前接口虽然用数组承载，但官方仅建议传入一个链接对象。
    type: CellTextType = Field(default=CellTextType.URL, description="固定为 url")
    text: Optional[str] = Field(default=None, description="展示文本")
    link: Optional[str] = Field(default=None, description="链接地址")


class CellLocationValue(WeComBaseModel):
    """地理位置单元格值。"""

    # 地理位置字段依赖固定键集合，禁止额外字段有助于区分联合类型。
    model_config = ConfigDict(extra="forbid")

    # 目前仅支持腾讯地图来源，文档约定固定传 `1`。
    source_type: Optional[CellLocationSourceType] = Field(
        default=None, description="地理位置来源类型"
    )
    id: Optional[str] = Field(default=None, description="位置对象 ID")
    latitude: Optional[str] = Field(default=None, description="纬度")
    longitude: Optional[str] = Field(default=None, description="经度")
    title: Optional[str] = Field(default=None, description="位置标题")


class CellAutoNumberValue(WeComBaseModel):
    """自动编号单元格值。"""

    # 自动编号对象字段固定，禁止额外字段可减少与其他对象数组混淆。
    model_config = ConfigDict(extra="forbid")

    # 序号的原始值。
    seq: Optional[str] = Field(default=None, description="自动编号原始序号")
    # 展示给用户看的格式化文本。
    text: Optional[str] = Field(default=None, description="自动编号展示文本")


# 记录单元格会随字段类型返回完全不同的 JSON 结构。
# 调用方通常需要结合字段元信息中的 `field_type` 来解释实际值形态。
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

# key 可以是字段标题，也可以是字段 ID，具体取决于请求里的 `key_type`。
RecordValues = Dict[str, CellValue]
# 查询记录时，企业微信可能会对空单元格直接返回 `null`。
QueryCellValue = CellValue | None
QueryRecordValues = Dict[str, QueryCellValue]


class AddRecord(WeComBaseModel):
    """新增记录项。"""

    values: RecordValues = Field(description="记录字段值")


class UpdateRecord(WeComBaseModel):
    """更新记录项。"""

    record_id: str = Field(description="记录 ID")
    values: RecordValues = Field(description="记录字段值")


class CommonRecord(WeComBaseModel):
    """新增/更新记录接口共用的记录结构。"""

    record_id: str = Field(description="记录 ID")
    values: RecordValues = Field(description="记录字段值")


class Record(CommonRecord):
    """查询记录接口返回的完整记录结构。"""

    # 查询接口返回的空单元格可能为 `null`，因此查询侧的 values 需要允许 `None`。
    values: QueryRecordValues
    create_time: Optional[str] = None
    update_time: Optional[str] = None
    creator_name: Optional[str] = None
    updater_name: Optional[str] = None


class Sort(WeComBaseModel):
    """记录查询排序项。"""

    # 官方接口按字段标题指定排序列，而不是字段 ID。
    field_title: str
    desc: Optional[bool] = None


class AddRecordsRequest(WeComBaseModel):
    """添加记录请求体。

    官方建议单次新增控制在 500 行内，且不能给创建时间、最后编辑时间、
    创建人、最后编辑人这四类系统字段写入值。
    """

    docid: str
    sheet_id: str
    # 控制 `values` 中使用字段标题还是字段 ID 作为 key。
    key_type: Optional[CellValueKeyType] = None
    records: List[AddRecord]


class AddRecordsResponse(WeComBaseResponse):
    """添加记录响应体。"""

    records: Optional[List[CommonRecord]] = None


class UpdateRecordsRequest(WeComBaseModel):
    """更新记录请求体。

    官方建议单次更新控制在 500 行内，且不能更新系统自动维护的时间/人员字段。
    """

    docid: str
    sheet_id: str
    key_type: Optional[CellValueKeyType] = None
    records: List[UpdateRecord]


class UpdateRecordsResponse(WeComBaseResponse):
    """更新记录响应体。"""

    records: Optional[List[CommonRecord]] = None


class DeleteRecordsRequest(WeComBaseModel):
    """删除记录请求体。"""

    docid: str
    sheet_id: str
    # 官方建议单次删除控制在 500 行内。
    record_ids: List[str]


class DeleteRecordsResponse(WeComBaseResponse):
    """删除记录响应体。"""

    pass


class GetRecordsRequest(WeComBaseModel):
    """查询记录请求体。"""

    docid: str
    sheet_id: str
    # 传入视图后，将以该视图上下文查询记录。
    view_id: Optional[str] = None
    record_ids: Optional[List[str]] = None
    # 控制返回记录中 `values` 的 key 使用字段标题还是字段 ID。
    key_type: Optional[CellValueKeyType] = None
    # 仅当 `key_type` 为字段标题模式时生效。
    field_titles: Optional[List[str]] = None
    # 仅当 `key_type` 为字段 ID 模式时生效。
    field_ids: Optional[List[str]] = None
    sort: Optional[List[Sort]] = None
    offset: Optional[int] = None
    # 单次 `limit` 最大为 1000；为空或为 0 时由接口按默认规则返回。
    limit: Optional[int] = None
    # 数据版本号，可用于做并发控制或增量判断。
    ver: Optional[int] = None
    # 官方文档说明 `filter_spec` 与 `sort` 不能同时使用。
    filter_spec: Optional[FilterSpec] = None


class GetRecordsResponse(WeComBaseResponse):
    """查询记录响应体。"""

    total: Optional[int] = None
    has_more: Optional[bool] = None
    next: Optional[int] = None
    records: Optional[List[Record]] = None
    # 与请求中的 `ver` 对应，可用于后续版本比较。
    ver: Optional[int] = None
