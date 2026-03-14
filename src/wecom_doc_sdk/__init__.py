"""企业微信文档 SDK 入口。

根包仅导出入口级对象，便于快速定位客户端；异常与请求/响应模型请从对应子模块导入。
"""

from .client import AccessTokenProvider, WeComClient

__all__ = ["AccessTokenProvider", "WeComClient"]
