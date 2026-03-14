from __future__ import annotations

from typing import Optional

from pydantic import BaseModel, ConfigDict


class WeComBaseModel(BaseModel):
    """SDK 内部基础模型，统一配置。"""

    model_config = ConfigDict(
        extra="ignore", populate_by_name=True, str_strip_whitespace=True
    )


class WeComBaseResponse(WeComBaseModel):
    """企业微信通用响应结构。"""

    errcode: int = 0
    errmsg: str = ""

    @property
    def ok(self) -> bool:
        return self.errcode == 0


class PageInfo(WeComBaseModel):
    """分页信息。"""

    total: Optional[int] = None
    has_more: Optional[bool] = None
    next: Optional[int] = None
