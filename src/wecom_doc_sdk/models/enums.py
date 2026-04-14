from __future__ import annotations

from enum import Enum, IntEnum


class StrEnum(str, Enum):
    """字符串枚举基类，便于 JSON 序列化。"""


class FieldType(StrEnum):
    """智能表字段类型枚举。

    用于字段定义、字段查询结果以及筛选条件中的 `field_type`。
    """

    FIELD_TYPE_TEXT = "FIELD_TYPE_TEXT"
    FIELD_TYPE_NUMBER = "FIELD_TYPE_NUMBER"
    FIELD_TYPE_CHECKBOX = "FIELD_TYPE_CHECKBOX"
    FIELD_TYPE_DATE_TIME = "FIELD_TYPE_DATE_TIME"
    FIELD_TYPE_IMAGE = "FIELD_TYPE_IMAGE"
    FIELD_TYPE_ATTACHMENT = "FIELD_TYPE_ATTACHMENT"
    FIELD_TYPE_USER = "FIELD_TYPE_USER"
    FIELD_TYPE_URL = "FIELD_TYPE_URL"
    FIELD_TYPE_SELECT = "FIELD_TYPE_SELECT"
    FIELD_TYPE_CREATED_USER = "FIELD_TYPE_CREATED_USER"
    FIELD_TYPE_MODIFIED_USER = "FIELD_TYPE_MODIFIED_USER"
    FIELD_TYPE_CREATED_TIME = "FIELD_TYPE_CREATED_TIME"
    FIELD_TYPE_MODIFIED_TIME = "FIELD_TYPE_MODIFIED_TIME"
    FIELD_TYPE_PROGRESS = "FIELD_TYPE_PROGRESS"
    FIELD_TYPE_PHONE_NUMBER = "FIELD_TYPE_PHONE_NUMBER"
    FIELD_TYPE_EMAIL = "FIELD_TYPE_EMAIL"
    FIELD_TYPE_SINGLE_SELECT = "FIELD_TYPE_SINGLE_SELECT"
    FIELD_TYPE_REFERENCE = "FIELD_TYPE_REFERENCE"
    FIELD_TYPE_LOCATION = "FIELD_TYPE_LOCATION"
    FIELD_TYPE_FORMULA = "FIELD_TYPE_FORMULA"
    FIELD_TYPE_CURRENCY = "FIELD_TYPE_CURRENCY"
    FIELD_TYPE_WWGROUP = "FIELD_TYPE_WWGROUP"
    FIELD_TYPE_AUTONUMBER = "FIELD_TYPE_AUTONUMBER"
    FIELD_TYPE_PERCENTAGE = "FIELD_TYPE_PERCENTAGE"
    FIELD_TYPE_BARCODE = "FIELD_TYPE_BARCODE"


class ViewType(StrEnum):
    """智能表视图类型枚举。"""

    VEW_UNKNOWN = "VEW_UNKNOWN"
    VIEW_TYPE_GRID = "VIEW_TYPE_GRID"
    VIEW_TYPE_KANBAN = "VIEW_TYPE_KANBAN"
    VIEW_TYPE_GALLERY = "VIEW_TYPE_GALLERY"
    VIEW_TYPE_GANTT = "VIEW_TYPE_GANTT"
    VIEW_TYPE_CALENDAR = "VIEW_TYPE_CALENDAR"


class CellValueKeyType(StrEnum):
    """记录 `values` 字典的 key 表示方式。"""

    CELL_VALUE_KEY_TYPE_FIELD_TITLE = "CELL_VALUE_KEY_TYPE_FIELD_TITLE"
    CELL_VALUE_KEY_TYPE_FIELD_ID = "CELL_VALUE_KEY_TYPE_FIELD_ID"


class Operator(StrEnum):
    """筛选条件支持的操作符。"""

    OPERATOR_UNKNOWN = "OPERATOR_UNKNOWN"
    OPERATOR_IS = "OPERATOR_IS"
    OPERATOR_IS_NOT = "OPERATOR_IS_NOT"
    OPERATOR_CONTAINS = "OPERATOR_CONTAINS"
    OPERATOR_DOES_NOT_CONTAIN = "OPERATOR_DOES_NOT_CONTAIN"
    OPERATOR_IS_GREATER = "OPERATOR_IS_GREATER"
    OPERATOR_IS_GREATER_OR_EQUAL = "OPERATOR_IS_GREATER_OR_EQUAL"
    OPERATOR_IS_LESS = "OPERATOR_IS_LESS"
    OPERATOR_IS_LESS_OR_EQUAL = "OPERATOR_IS_LESS_OR_EQUAL"
    OPERATOR_IS_EMPTY = "OPERATOR_IS_EMPTY"
    OPERATOR_IS_NOT_EMPTY = "OPERATOR_IS_NOT_EMPTY"


class DateTimeType(StrEnum):
    """日期筛选值类型。"""

    DATE_TIME_TYPE_DETAIL_DATE = "DATE_TIME_TYPE_DETAIL_DATE"
    DATE_TIME_TYPE_TODAY = "DATE_TIME_TYPE_TODAY"
    DATE_TIME_TYPE_TOMORROW = "DATE_TIME_TYPE_TOMORROW"
    DATE_TIME_TYPE_YESTERDAY = "DATE_TIME_TYPE_YESTERDAY"
    DATE_TIME_TYPE_CURRENT_WEEK = "DATE_TIME_TYPE_CURRENT_WEEK"
    DATE_TIME_TYPE_LAST_WEEK = "DATE_TIME_TYPE_LAST_WEEK"
    DATE_TIME_TYPE_CURRENT_MONTH = "DATE_TIME_TYPE_CURRENT_MONTH"
    DATE_TIME_TYPE_THE_PAST_7_DAYS = "DATE_TIME_TYPE_THE_PAST_7_DAYS"
    DATE_TIME_TYPE_THE_NEXT_7_DAYS = "DATE_TIME_TYPE_THE_NEXT_7_DAYS"
    DATE_TIME_TYPE_LAST_MONTH = "DATE_TIME_TYPE_LAST_MONTH"
    DATE_TIME_TYPE_THE_PAST_30_DAYS = "DATE_TIME_TYPE_THE_PAST_30_DAYS"
    DATE_TIME_TYPE_THE_NEXT_30_DAYS = "DATE_TIME_TYPE_THE_NEXT_30_DAYS"


class Conjunction(StrEnum):
    """多个筛选条件的连接关系。"""

    CONJUNCTION_AND = "CONJUNCTION_AND"
    CONJUNCTION_OR = "CONJUNCTION_OR"


class ViewColorConditionType(StrEnum):
    """视图填色作用范围。"""

    VIEW_COLOR_CONDITION_TYPE_ROW = "VIEW_COLOR_CONDITION_TYPE_ROW"
    VIEW_COLOR_CONDITION_TYPE_COLUMN = "VIEW_COLOR_CONDITION_TYPE_COLUMN"
    VIEW_COLOR_CONDITION_TYPE_CELL = "VIEW_COLOR_CONDITION_TYPE_CELL"


class ViewColor(StrEnum):
    """视图条件填色的可选颜色值。

    这些值需要原样透传给企业微信接口，不建议自行改写。
    """

    fillColorGray_5 = "fillColorGray_5"
    accentBlueLighten_5 = "accentBlueLighten_5"
    chromeCyanLighten_5 = "chromeCyanLighten_5"
    chromeMintLighten_5 = "chromeMintLighten_5"
    chromeRedLighten_5 = "chromeRedLighten_5"
    chromeOrangeLighten_5 = "chromeOrangeLighten_5"
    chromeAmberLighten_5 = "chromeAmberLighten_5"
    chromeVioletLighten_5 = "chromeVioletLighten_5"
    chromePinkLighten_5 = "chromePinkLighten_5"
    fillColorGray_4 = "fillColorGray_4"
    accentBlueLighten_4 = "accentBlueLighten_4"
    chromeCyanLighten_4 = "chromeCyanLighten_4"
    chromeMintLighten_4 = "chromeMintLighten_4"
    chromeRedLighten_4 = "chromeRedLighten_4"
    chromeOrangeLighten_4 = "chromeOrangeLighten_4"
    chromeAmberLighten_4 = "chromeAmberLighten_4"
    chromeVioletLighten_4 = "chromeVioletLighten_4"
    chromePinkLighten_4 = "chromePinkLighten_4"
    fillColorGray_3 = "fillColorGray_3"
    accentBlueLighten_3 = "accentBlueLighten_3"
    chromeCyanLighten_3 = "chromeCyanLighten_3"
    chromeMintLighten_3 = "chromeMintLighten_3"
    chromeRedLighten_3 = "chromeRedLighten_3"
    chromeOrangeLighten_3 = "chromeOrangeLighten_3"
    chromeAmberLighten_3 = "chromeAmberLighten_3"
    chromeVioletLighten_3 = "chromeVioletLighten_3"
    chromePinkLighten_3 = "chromePinkLighten_3"


class LinkType(StrEnum):
    """超链接字段的展示样式。"""

    LINK_TYPE_PURE_TEXT = "LINK_TYPE_PURE_TEXT"
    LINK_TYPE_ICON_TEXT = "LINK_TYPE_ICON_TEXT"


class DisplayMode(StrEnum):
    """文件字段等场景的展示模式。"""

    DISPLAY_MODE_LIST = "DISPLAY_MODE_LIST"
    DISPLAY_MODE_GRID = "DISPLAY_MODE_GRID"


class LocationInputType(StrEnum):
    """地理位置字段的输入方式。"""

    LOCATION_INPUT_TYPE_MANUAL = "LOCATION_INPUT_TYPE_MANUAL"
    LOCATION_INPUT_TYPE_AUTO = "LOCATION_INPUT_TYPE_AUTO"


class NumberType(StrEnum):
    """自动编号字段的编号模式。"""

    NUMBER_TYPE_INCR = "NUMBER_TYPE_INCR"
    NUMBER_TYPE_CUSTOM = "NUMBER_TYPE_CUSTOM"


class NumberRuleType(StrEnum):
    """自动编号规则项类型。"""

    NUMBER_RULE_TYPE_INCR = "NUMBER_RULE_TYPE_INCR"
    NUMBER_RULE_TYPE_FIXED_CHAR = "NUMBER_RULE_TYPE_FIXED_CHAR"
    NUMBER_RULE_TYPE_TIME = "NUMBER_RULE_TYPE_TIME"


class CurrencyType(StrEnum):
    """货币字段支持的货币符号类型。成员值为官方货币编码。"""

    CURRENCY_TYPE_CNY = "CURRENCY_TYPE_CNY"
    CURRENCY_TYPE_USD = "CURRENCY_TYPE_USD"
    CURRENCY_TYPE_EUR = "CURRENCY_TYPE_EUR"
    CURRENCY_TYPE_GBP = "CURRENCY_TYPE_GBP"
    CURRENCY_TYPE_JPY = "CURRENCY_TYPE_JPY"
    CURRENCY_TYPE_KRW = "CURRENCY_TYPE_KRW"
    CURRENCY_TYPE_HKD = "CURRENCY_TYPE_HKD"
    CURRENCY_TYPE_MOP = "CURRENCY_TYPE_MOP"
    CURRENCY_TYPE_TWD = "CURRENCY_TYPE_TWD"
    CURRENCY_TYPE_AED = "CURRENCY_TYPE_AED"
    CURRENCY_TYPE_AUD = "CURRENCY_TYPE_AUD"
    CURRENCY_TYPE_BRL = "CURRENCY_TYPE_BRL"
    CURRENCY_TYPE_CAD = "CURRENCY_TYPE_CAD"
    CURRENCY_TYPE_CHF = "CURRENCY_TYPE_CHF"
    CURRENCY_TYPE_IDR = "CURRENCY_TYPE_IDR"
    CURRENCY_TYPE_INR = "CURRENCY_TYPE_INR"
    CURRENCY_TYPE_MXN = "CURRENCY_TYPE_MXN"
    CURRENCY_TYPE_MYR = "CURRENCY_TYPE_MYR"
    CURRENCY_TYPE_PHP = "CURRENCY_TYPE_PHP"
    CURRENCY_TYPE_PLN = "CURRENCY_TYPE_PLN"
    CURRENCY_TYPE_RUB = "CURRENCY_TYPE_RUB"
    CURRENCY_TYPE_SGD = "CURRENCY_TYPE_SGD"
    CURRENCY_TYPE_THB = "CURRENCY_TYPE_THB"
    CURRENCY_TYPE_TRY = "CURRENCY_TYPE_TRY"
    CURRENCY_TYPE_VND = "CURRENCY_TYPE_VND"


class SheetType(StrEnum):
    """子表类型。

    主要出现在查询子表接口返回中，用于区分普通智能表、仪表盘和说明页。
    """

    dashboard = "dashboard"
    external = "external"
    smartsheet = "smartsheet"


class WedriveFileType(IntEnum):
    """微盘 `file_create` 支持的文件类型。"""

    FOLDER = 1
    DOC = 3
    SHEET = 4


class DecimalPlaces(IntEnum):
    """数字、进度、货币、百分比等字段的小数位设置。"""

    SHOW_ORIGIN = -1
    INT = 0
    ONE = 1
    TWO = 2
    THREE = 3
    FOUR = 4


class Style(IntEnum):
    """单选/多选选项颜色编号。

    企业微信接口使用数值而非语义名称表示色板，这里保留官方编号并补充中文说明。
    """

    STYLE_1 = 1  # 浅红1
    STYLE_2 = 2  # 浅橙1
    STYLE_3 = 3  # 浅天蓝1
    STYLE_4 = 4  # 浅绿1
    STYLE_5 = 5  # 浅紫1
    STYLE_6 = 6  # 浅粉红1
    STYLE_7 = 7  # 浅灰1
    STYLE_8 = 8  # 白
    STYLE_9 = 9  # 灰
    STYLE_10 = 10  # 浅蓝1
    STYLE_11 = 11  # 浅蓝2
    STYLE_12 = 12  # 蓝
    STYLE_13 = 13  # 浅天蓝2
    STYLE_14 = 14  # 天蓝
    STYLE_15 = 15  # 浅绿2
    STYLE_16 = 16  # 绿
    STYLE_17 = 17  # 浅红2
    STYLE_18 = 18  # 红
    STYLE_19 = 19  # 浅橙2
    STYLE_20 = 20  # 橙
    STYLE_21 = 21  # 浅黄1
    STYLE_22 = 22  # 浅黄2
    STYLE_23 = 23  # 黄
    STYLE_24 = 24  # 浅紫2
    STYLE_25 = 25  # 紫
    STYLE_26 = 26  # 浅粉红2
    STYLE_27 = 27  # 粉红


class DocType(IntEnum):
    """文档类型枚举。`3=文档`、`4=表格`、`10=智能表格`。"""

    DOC = 3
    SHEET = 4
    SMARTSHEET = 10


class DocMemberType(IntEnum):
    """文档成员类型。"""

    USER = 1
    DEPARTMENT = 2


class DocMemberAuth(IntEnum):
    """文档成员权限类型。"""

    READONLY = 1
    READWRITE = 2
    ADMIN = 7


class SheetPrivRuleType(IntEnum):
    """智能表内容权限规则类型。"""

    ALL_MEMBERS = 1
    EXTRA = 2


class SheetPrivType(IntEnum):
    """智能表子表内容权限类型。"""

    ALL = 1
    EDITABLE = 2
    VIEW_ONLY = 3
    NONE = 4


class SheetPrivFieldRangeType(IntEnum):
    """字段权限作用范围。"""

    ALL_FIELDS = 1
    PART_FIELDS = 2


class SheetPrivRecordRangeType(IntEnum):
    """记录权限作用范围。"""

    ALL_RECORDS = 1
    ANY_CONDITION = 2
    ALL_CONDITIONS = 3


class SheetPrivRecordOperType(IntEnum):
    """记录条件判断类型。"""

    CONTAINS_SELF = 1
    CONTAINS_VALUE = 2
    NOT_CONTAINS_VALUE = 3
    EQUALS_VALUE = 4
    NOT_EQUALS_VALUE = 5
    IS_EMPTY = 6
    NOT_EMPTY = 7


class SheetPrivRecordOtherPriv(IntEnum):
    """记录不满足条件时的权限。"""

    NOT_EDITABLE = 1
    NOT_VISIBLE = 2


class DocJoinRuleAuth(IntEnum):
    """文档加入后可获得的权限类型。"""

    READONLY = 1
    READWRITE = 2


class CoAuthType(IntEnum):
    """文档查看权限的共享对象类型。"""

    DEPARTMENT = 2


class DocWatermarkMarginType(IntEnum):
    """文档水印边距样式。"""

    TYPE_1 = 1
    TYPE_2 = 2


class CellTextType(StrEnum):
    """文本单元格对象类型。"""

    TEXT = "text"
    URL = "url"


class CellAttachmentDocType(IntEnum):
    """附件对象类型。"""

    FOLDER = 1
    FILE = 2


class CellLocationSourceType(IntEnum):
    """地理位置来源类型。"""

    TENCENT_MAP = 1


class CellUserIdType(IntEnum):
    """人员值来源类型。"""

    USER = 1
    TMP_EXTERNAL_USER = 2
    AGENT = 3
    SYSTEM = 4


class DocumentNodeType(StrEnum):
    """文档节点类型。"""

    DOCUMENT = "Document"
    MAIN_STORY = "MainStory"
    SECTION = "Section"
    PARAGRAPH = "Paragraph"
    TABLE = "Table"
    TABLE_ROW = "TableRow"
    TABLE_CELL = "TableCell"
    TEXT = "Text"
    DRAWING = "Drawing"
