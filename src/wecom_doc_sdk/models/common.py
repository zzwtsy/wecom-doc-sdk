from __future__ import annotations

from typing import Optional

from pydantic import BaseModel, ConfigDict


class WeComBaseModel(BaseModel):
    """SDK 内部基础模型，统一配置。

    统一忽略额外字段、允许通过别名填充、并自动裁剪字符串首尾空白，
    以适配企业微信接口中常见的向后兼容字段和输入噪声。
    """

    model_config = ConfigDict(
        extra="ignore", populate_by_name=True, str_strip_whitespace=True
    )


class WeComBaseResponse(WeComBaseModel):
    """企业微信通用响应结构。"""

    errcode: int = 0
    errmsg: str = ""

    @property
    def ok(self) -> bool:
        """当前响应是否业务成功。

        企业微信官方约定 `errcode == 0` 表示成功，不应依赖 `errmsg` 文案做判断。
        """

        return self.errcode == 0


class PageInfo(WeComBaseModel):
    """分页信息。

    适用于企业微信返回 `total/has_more/next` 的列表查询接口。
    """

    # 当前查询条件下的总记录数，通常是筛选后的结果总量。
    total: Optional[int] = None
    # 是否还有下一页数据可继续拉取。
    has_more: Optional[bool] = None
    # 下一次查询应使用的偏移量。
    next: Optional[int] = None
