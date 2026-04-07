from __future__ import annotations

from typing import List, Optional

from pydantic import AliasChoices, Field, model_validator
from pydantic import Field as PydanticField

from .common import WeComBaseModel, WeComBaseResponse
from .enums import DocumentNodeType


class Location(WeComBaseModel):
    """文档中的位置索引。"""

    index: int = Field(description="文档位置索引")


class Range(WeComBaseModel):
    """从起始索引开始的一段范围。"""

    start_index: int = Field(description="起始索引")
    length: int = Field(description="长度")


class TextProperty(WeComBaseModel):
    """文本属性。"""

    bold: Optional[bool] = Field(default=None, description="是否加粗")
    color: Optional[str] = Field(default=None, description="文字颜色（RRGGBB）")
    background_color: Optional[str] = Field(
        default=None, description="文字背景色（RRGGBB）"
    )


class ReplaceText(WeComBaseModel):
    """替换指定范围文本。"""

    text: str = Field(description="替换后的文本")
    ranges: List[Range] = Field(description="替换范围列表")


class InsertText(WeComBaseModel):
    """在指定位置插入文本。"""

    text: str = Field(description="插入文本")
    location: Location = Field(description="插入位置")


class DeleteContent(WeComBaseModel):
    """删除指定范围内容。"""

    range: Range = Field(description="删除范围")


class InsertImage(WeComBaseModel):
    """在指定位置插入图片。"""

    image_id: str = Field(description="图片资源 ID 或 URL")
    location: Location = Field(description="插入位置")
    width: Optional[int] = Field(default=None, description="图片宽度（像素）")
    height: Optional[int] = Field(default=None, description="图片高度（像素）")


class InsertPageBreak(WeComBaseModel):
    """在指定位置插入分页符。"""

    location: Location = Field(description="分页符插入位置")


class InsertTable(WeComBaseModel):
    """在指定位置插入表格。"""

    rows: int = Field(description="表格行数")
    cols: int = Field(description="表格列数")
    location: Location = Field(description="插入位置")


class InsertParagraph(WeComBaseModel):
    """在指定位置插入段落。"""

    location: Location = Field(description="段落插入位置")


class UpdateTextProperty(WeComBaseModel):
    """更新文本属性。"""

    text_property: TextProperty = Field(description="目标文本属性")
    ranges: List[Range] = Field(description="应用范围列表")


class UpdateRequest(WeComBaseModel):
    """单个批量更新操作。"""

    replace_text: Optional[ReplaceText] = Field(
        default=None, description="替换文本操作"
    )
    insert_text: Optional[InsertText] = Field(default=None, description="插入文本操作")
    delete_content: Optional[DeleteContent] = Field(
        default=None, description="删除内容操作"
    )
    insert_image: Optional[InsertImage] = Field(
        default=None, description="插入图片操作"
    )
    insert_page_break: Optional[InsertPageBreak] = Field(
        default=None, description="插入分页符操作"
    )
    insert_table: Optional[InsertTable] = Field(
        default=None, description="插入表格操作"
    )
    insert_paragraph: Optional[InsertParagraph] = Field(
        default=None, description="插入段落操作"
    )
    update_text_property: Optional[UpdateTextProperty] = Field(
        default=None, description="更新文本属性操作"
    )

    @model_validator(mode="after")
    def validate_exactly_one_operation(self) -> "UpdateRequest":
        """单次更新仅允许声明一个操作。"""

        op_count = sum(
            value is not None
            for value in (
                self.replace_text,
                self.insert_text,
                self.delete_content,
                self.insert_image,
                self.insert_page_break,
                self.insert_table,
                self.insert_paragraph,
                self.update_text_property,
            )
        )
        if op_count != 1:
            raise ValueError("requests 中每个操作对象必须且只能包含一个操作")
        return self


class SectionProperty(WeComBaseModel):
    """Section 节点属性。"""


class ParagraphProperty(WeComBaseModel):
    """Paragraph 节点属性。"""


class RunProperty(WeComBaseModel):
    """Text 节点属性。"""


class TableProperty(WeComBaseModel):
    """Table 节点属性。"""


class TableRowProperty(WeComBaseModel):
    """TableRow 节点属性。"""


class TableCellProperty(WeComBaseModel):
    """TableCell 节点属性。"""


class DrawingProperty(WeComBaseModel):
    """Drawing 节点属性。"""


class DocumentNodeProperty(WeComBaseModel):
    """节点属性容器。"""

    section_property: Optional[SectionProperty] = Field(
        default=None, description="节属性"
    )
    paragraph_property: Optional[ParagraphProperty] = Field(
        default=None, description="段落属性"
    )
    run_property: Optional[RunProperty] = Field(default=None, description="文本属性")
    table_property: Optional[TableProperty] = Field(
        default=None, description="表格属性"
    )
    table_row_property: Optional[TableRowProperty] = Field(
        default=None, description="表格行属性"
    )
    table_cell_property: Optional[TableCellProperty] = Field(
        default=None, description="表格单元格属性"
    )
    drawing_property: Optional[DrawingProperty] = Field(
        default=None, description="图形属性"
    )


class DocumentNode(WeComBaseModel):
    """文档节点。"""

    begin: Optional[int] = Field(default=None, description="节点起始位置")
    end: Optional[int] = Field(default=None, description="节点结束位置")
    property: Optional[DocumentNodeProperty] = Field(
        default=None, description="节点属性"
    )
    type: Optional[DocumentNodeType] = Field(default=None, description="节点类型")
    children: Optional[List["DocumentNode"]] = Field(
        default=None, description="子节点列表"
    )
    text: Optional[str] = Field(default=None, description="文本内容（文本节点有效）")


class GetDocumentRequest(WeComBaseModel):
    """获取文档数据请求体。"""

    docid: str = Field(description="文档 ID")


class GetDocumentResponse(WeComBaseResponse):
    """获取文档数据响应体。"""

    version: Optional[int] = Field(default=None, description="文档版本号")
    document: Optional[DocumentNode] = Field(default=None, description="文档根节点")


class BatchUpdateDocumentRequest(WeComBaseModel):
    """批量编辑文档内容请求体。"""

    docid: str = Field(description="文档 ID")
    # 官方示例里偶发 `verison` 拼写，兼容输入但统一按 `version` 出参。
    version: Optional[int] = PydanticField(
        default=None, validation_alias=AliasChoices("version", "verison")
    )
    requests: List[UpdateRequest] = Field(description="批量更新操作列表")


class BatchUpdateDocumentResponse(WeComBaseResponse):
    """批量编辑文档内容响应体。"""

    pass
