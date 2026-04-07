# 企业微信文档 SDK

> [!WARNING]
> 本项目为 **100% vibe coding** 实验产物，仅用于学习与测试交流；**请勿直接用于生产环境项目**。

`wecom-doc-sdk` 是一个面向企业微信文档相关服务端 API 的 Python SDK，当前已支持“文档管理”“文档内容”“管理智能表格内容”与“设置文档权限”中的部分能力，并为后续扩展更多文档接口保留了清晰的客户端与模型结构。

## 特性

- 基于 `httpx.Client` 的同步客户端，复用连接并统一处理超时
- 内置 `access_token` 获取、缓存和提前刷新逻辑
- 使用 `pydantic v2` 建模请求与响应，便于校验和序列化
- 完整类型标注，适合编辑器补全与静态检查
- 对企业微信业务错误与请求错误做了统一异常封装
- 代码和公开模型带中文注释，尽量降低接入与维护成本

## 当前支持

当前已封装企业微信以下能力：

- 文档管理
- 新建文档/表格/智能表格
- 获取文档基础信息
- 获取分享链接
- 重命名文档
- 删除文档
- 文档内容
- 获取文档内容
- 批量编辑文档内容
- 管理智能表格内容
- 子表：添加、删除、更新、查询
- 视图：添加、删除、更新、查询
- 字段：添加、删除、更新、查询
- 记录：添加、删除、更新、查询
- 编组：添加、更新、删除、查询
- 设置文档权限
- 获取文档权限信息
- 修改文档加入规则
- 修改文档成员与权限
- 修改文档安全设置

对应入口为 `WeComClient.documents`、`WeComClient.document_content`、`WeComClient.smartsheet` 与 `WeComClient.permissions`。

## 安装

要求 Python `3.10+`。

使用 `pip`：

```bash
pip install wecom-doc-sdk
```

使用 `uv`：

```bash
uv add wecom-doc-sdk
```

如果是本地开发安装：

```bash
uv sync --dev
```

## 快速开始

### 创建客户端

```python
from wecom_doc_sdk import WeComClient

with WeComClient(
    corp_id="YOUR_CORP_ID",
    corp_secret="YOUR_CORP_SECRET",
) as client:
    sheets = client.smartsheet.get_sheet({"docid": "DOCID"})
    print(sheets.ok, sheets.sheet_list)
```

### 查询文档权限信息

```python
from wecom_doc_sdk import WeComClient

with WeComClient(
    corp_id="YOUR_CORP_ID",
    corp_secret="YOUR_CORP_SECRET",
) as client:
    response = client.permissions.get_doc_auth({"docid": "DOCID"})

    print(response.ok, response.access_rule, response.secure_setting)
```

### 创建文档并获取分享链接

```python
from wecom_doc_sdk import WeComClient
from wecom_doc_sdk.models.documents import DocType

with WeComClient(
    corp_id="YOUR_CORP_ID",
    corp_secret="YOUR_CORP_SECRET",
) as client:
    created = client.documents.create_doc(
        {
            "spaceid": "SPACEID",
            "fatherid": "FATHERID",
            "doc_type": DocType.DOC,
            "title": "项目周报",
        }
    )
    share = client.documents.doc_share({"docid": created.docid})
    print(created.ok, created.docid, share.share_url)
```

### 获取文档内容

```python
from wecom_doc_sdk import WeComClient

with WeComClient(
    corp_id="YOUR_CORP_ID",
    corp_secret="YOUR_CORP_SECRET",
) as client:
    response = client.document_content.get({"docid": "DOCID"})
    print(response.ok, response.content is not None)
```

### 使用 Pydantic 模型查询字段

```python
from wecom_doc_sdk import WeComClient
from wecom_doc_sdk.models.fields import GetFieldsRequest

with WeComClient(
    corp_id="YOUR_CORP_ID",
    corp_secret="YOUR_CORP_SECRET",
) as client:
    response = client.smartsheet.get_fields(
        GetFieldsRequest(
            docid="DOCID",
            sheet_id="SHEET_ID",
            limit=100,
        )
    )

    if response.fields:
        for field in response.fields:
            print(field.field_id, field.field_title, field.field_type)
```

### 直接使用 `dict` 新增记录

SDK 的公开 API 同时接受 Pydantic 模型或 `dict`。

```python
from wecom_doc_sdk import WeComClient

with WeComClient(
    corp_id="YOUR_CORP_ID",
    corp_secret="YOUR_CORP_SECRET",
) as client:
    response = client.smartsheet.add_records(
        {
            "docid": "DOCID",
            "sheet_id": "SHEET_ID",
            "records": [
                {
                    "values": {
                        "标题": [{"type": "text", "text": "第一条任务"}],
                        "进度": 50,
                    }
                }
            ],
        }
    )

    print(response.ok, response.records)
```

## 错误处理

SDK 将错误分成两类：

- `WeComAPIError`：企业微信接口已返回响应，但 `errcode != 0`
- `WeComRequestError`：网络异常、HTTP 状态异常或响应解析失败

推荐按下面的方式处理：

```python
from wecom_doc_sdk import WeComClient
from wecom_doc_sdk.exceptions import WeComAPIError, WeComRequestError

try:
    with WeComClient(
        corp_id="YOUR_CORP_ID",
        corp_secret="YOUR_CORP_SECRET",
    ) as client:
        client.smartsheet.get_sheet({"docid": "DOCID"})
except WeComAPIError as exc:
    print("业务错误", exc.errcode, exc.errmsg)
    print("原始响应", exc.raw)
except WeComRequestError as exc:
    print("请求失败", exc)
    print("底层原因", exc.cause)
```

## 设计约定

- `access_token` 仅在服务端获取和缓存，不应返回给前端
- 业务成功与否始终以 `errcode` 判断，不应依赖 `errmsg` 文案
- 所有请求统一通过 `WeComClient.request_json()` 注入 `access_token`
- 所有模型统一通过 `model_dump(by_alias=True, exclude_none=True)` 序列化
- 当前客户端为同步版；如后续需要，可在现有结构上扩展异步能力

## 导入建议

为避免根包导出过多类型，推荐按职责导入：

- 根包 `wecom_doc_sdk`：`WeComClient`、`AccessTokenProvider`
- 异常：从 `wecom_doc_sdk.exceptions` 导入 `WeComAPIError`、`WeComRequestError`
- 文档权限模型：从 `wecom_doc_sdk.models.permissions` 导入
- 文档管理模型：从 `wecom_doc_sdk.models.documents` 导入
- 文档内容模型：从 `wecom_doc_sdk.models.document_content` 导入
- 子表模型：从 `wecom_doc_sdk.models.sheets` 导入
- 视图模型：从 `wecom_doc_sdk.models.views` 导入
- 字段模型：从 `wecom_doc_sdk.models.fields` 导入
- 记录模型：从 `wecom_doc_sdk.models.records` 导入
- 编组模型：从 `wecom_doc_sdk.models.groups` 导入

例如：`from wecom_doc_sdk.models.fields import GetFieldsRequest`

## 项目结构

```text
references/          # 官方文档入口与实现参考索引
src/wecom_doc_sdk/
├── apis/           # 接口封装
├── models/         # Pydantic 模型与枚举
├── client.py       # 客户端、鉴权与统一请求入口
└── exceptions.py   # 异常定义
```

维护时可参考 `references/wecom-docs.md` 中整理的官方文档入口与当前实现对应条目。

## 开发

安装开发依赖：

```bash
uv sync --dev
```

常用检查命令：

```bash
uv run ruff check .
uv run black --check .
uv run ty check
uv run pytest
```

## 发布

本地构建与检查：

```bash
uv build
uvx twine check dist/*
```

发布到 TestPyPI：

```bash
uv publish --index testpypi
```

发布到 PyPI：

```bash
uv publish
```

项目约定与贡献规范见 `CONTRIBUTING.md`。

## 适用范围

这个库当前聚焦企业微信文档能力，已覆盖文档管理、文档内容、智能表格内容管理和部分文档权限管理。后续可以在保持现有客户端与模型风格一致的前提下，继续扩展更多企业微信文档相关 API 模块。
