# 企业微信文档 SDK

`wecom-doc-sdk` 是一个面向企业微信文档相关服务端 API 的 Python SDK，当前聚焦“文档 -> 管理智能表格内容”能力，并为后续扩展更多文档接口保留了清晰的客户端与模型结构。

## 特性

- 基于 `httpx.Client` 的同步客户端，复用连接并统一处理超时
- 内置 `access_token` 获取、缓存和提前刷新逻辑
- 使用 `pydantic v2` 建模请求与响应，便于校验和序列化
- 完整类型标注，适合编辑器补全与静态检查
- 对企业微信业务错误与请求错误做了统一异常封装
- 代码和公开模型带中文注释，尽量降低接入与维护成本

## 当前支持

当前已封装企业微信“管理智能表格内容”中的以下能力：

- 子表：添加、删除、更新、查询
- 视图：添加、删除、更新、查询
- 字段：添加、删除、更新、查询
- 记录：添加、删除、更新、查询
- 编组：添加、更新、删除、查询

对应入口为 `WeComClient.smartsheet`。

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
uv pip install -e .[dev]
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

### 使用 Pydantic 模型查询字段

```python
from wecom_doc_sdk import GetFieldsRequest, WeComClient

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
from wecom_doc_sdk import WeComAPIError, WeComRequestError, WeComClient

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

## 常用导出

根包 `wecom_doc_sdk` 已导出常用客户端、异常和请求/响应模型，例如：

- `WeComClient`
- `AccessTokenProvider`
- `WeComAPIError`
- `WeComRequestError`
- `AddSheetRequest`
- `GetFieldsRequest`
- `AddRecordsRequest`
- `UpdateViewRequest`

更多模型可从 `wecom_doc_sdk.models` 导入。

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
uv pip install -e .[dev]
```

常用检查命令：

```bash
ruff check .
black --check .
ty check
pytest
```

项目约定与贡献规范见 `CONTRIBUTING.md`。

## 适用范围

这个库当前聚焦企业微信文档能力，尤其是智能表格内容管理，但项目结构已经按“可扩展库”来组织。后续可以在保持现有客户端与模型风格一致的前提下，继续扩展更多企业微信文档相关 API 模块。
