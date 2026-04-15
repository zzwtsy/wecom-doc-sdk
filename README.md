# 企业微信文档 SDK

> [!WARNING]
> 本项目为 **100% vibe coding** 实验产物，仅用于学习与测试交流；**请勿直接用于生产环境项目**。

`wecom-doc-sdk` 是一个面向企业微信文档相关服务端 API 的 Python SDK，当前已支持“文档管理”“文档内容”“管理智能表格内容”“微盘上传相关能力”与“设置文档权限”中的部分能力，并提供了 `wecom-doc-sdk` CLI 用于生成脚手架模板和批量创建智能表格资源。

## 特性

- 基于 `httpx.Client` 的同步客户端，复用连接并统一处理超时
- 内置 `access_token` 获取、缓存和提前刷新逻辑
- 使用 `pydantic v2` 建模请求与响应，便于校验和序列化
- 完整类型标注，适合编辑器补全与静态检查
- 对企业微信业务错误与请求错误做了统一异常封装
- 提供 `wecom-doc-sdk` CLI，可分别创建空间、目录、智能表格、子表，也可给已有空间/文档添加管理员，并支持通过脚手架批量创建资源
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
- 微盘与上传
- 文档图片上传
- 微盘文件上传
- 微盘空间：创建、成员添加、成员移除、空间信息查询
- 微盘文件：创建、分享链接、分块上传初始化、分块上传、分块上传完成
- 智能表格附件辅助上传
- 将微盘文件上传后写入附件字段
- 根据 `bytes` 内容自动选择直传或分块上传，再写入附件字段
- 设置文档权限
- 获取文档权限信息
- 修改文档加入规则
- 修改文档成员与权限
- 修改文档安全设置

对应入口为 `WeComClient.documents`、`WeComClient.document_content`、`WeComClient.smartsheet`、`WeComClient.uploads` 与 `WeComClient.permissions`。

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

安装完成后可直接使用 CLI：

```bash
wecom-doc-sdk --help
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
from wecom_doc_sdk.models.enums import DocType

with WeComClient(
    corp_id="YOUR_CORP_ID",
    corp_secret="YOUR_CORP_SECRET",
) as client:
    created = client.documents.create_doc(
        {
            "spaceid": "SPACEID",
            "fatherid": "FATHERID",
            "doc_type": DocType.DOC,
            "doc_name": "项目周报",
        }
    )
    share = client.documents.doc_share({"docid": created.docid})
    print(created.ok, created.docid, share.share_url)
```

### 使用 CLI 生成模板并创建资源

仓库内已经提供了可直接参考的静态模板，位于 `examples/cli/`：

- `examples/cli/scaffold.create.yaml`
- `examples/cli/scaffold.use_existing.yaml`
- `examples/cli/space.yaml`
- `examples/cli/folder.yaml`
- `examples/cli/smartsheet.yaml`
- `examples/cli/sheet.yaml`
- `examples/cli/space-admin.yaml`
- `examples/cli/doc-admin.yaml`

先生成一份脚手架模板：

```bash
wecom-doc-sdk template init scaffold template.yaml
```

命令成功后会输出 JSON，包含稳定字段：`status`、`action`、`path`。

如果你已经有现成的微盘空间和目录，也可以生成复用模式的脚手架模板：

```bash
wecom-doc-sdk template init scaffold template.yaml --mode use_existing
```

确认模板内容后，执行脚手架创建微盘空间、目录、智能表格、子表和字段：

```bash
wecom-doc-sdk scaffold template.yaml \
  --corp-id YOUR_CORP_ID \
  --corp-secret YOUR_CORP_SECRET
```

只想预览本次会创建什么资源时，可以先运行：

```bash
wecom-doc-sdk scaffold template.yaml \
  --dry-run
```

`scaffold --dry-run` 不要求鉴权参数，输出 JSON 会包含 `status`、`action`、`mode`、`path`、`template_path`、`manifest_path` 和 `actions`。

正式执行 `scaffold` 时，仍需提供 `--corp-id` 与 `--corp-secret`；成功后输出 JSON，包含 `status`、`action`、`path`、`manifest_path`、`template_path` 以及本次创建的关键资源标识。

如果你想分别创建资源，也可以使用独立命令。

生成空间模板并创建空间：

```bash
wecom-doc-sdk template init space space.yaml
wecom-doc-sdk space create space.yaml \
  --corp-id YOUR_CORP_ID \
  --corp-secret YOUR_CORP_SECRET
```

在已有空间下生成目录模板并创建目录：

```bash
wecom-doc-sdk template init folder folder.yaml
wecom-doc-sdk space folder create folder.yaml \
  --corp-id YOUR_CORP_ID \
  --corp-secret YOUR_CORP_SECRET
```

生成智能表格模板并创建智能表格：

```bash
wecom-doc-sdk template init smartsheet smartsheet.yaml
wecom-doc-sdk smartsheet create smartsheet.yaml \
  --corp-id YOUR_CORP_ID \
  --corp-secret YOUR_CORP_SECRET
```

生成子表模板并在已有智能表格中创建子表：

```bash
wecom-doc-sdk template init sheet sheet.yaml
wecom-doc-sdk smartsheet sheet create sheet.yaml \
  --corp-id YOUR_CORP_ID \
  --corp-secret YOUR_CORP_SECRET
```

生成空间管理员模板并给已有空间添加管理员：

```bash
wecom-doc-sdk template init space-admin space-admin.yaml
wecom-doc-sdk space admin add space-admin.yaml \
  --corp-id YOUR_CORP_ID \
  --corp-secret YOUR_CORP_SECRET
```

`space admin add` 的 JSON 输出会保留原有的 `admin_users`、`existing_admin_count`、`added_count`，并新增 `skipped_existing_admin_users` 与 `effective_added_count`，用于区分模板中的重复管理员和本次真正新增的人数。

生成文档管理员模板并给已有文档添加管理员：

```bash
wecom-doc-sdk template init doc-admin doc-admin.yaml
wecom-doc-sdk doc admin add doc-admin.yaml \
  --corp-id YOUR_CORP_ID \
  --corp-secret YOUR_CORP_SECRET
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

### 上传附件并写入智能表格

如果你已经有 `docid`、`sheet_id`、附件字段 ID，以及可上传的微盘位置，可以直接让 SDK 完成“上传到微盘 + 写入附件列”这条链路：

```python
from wecom_doc_sdk import WeComClient

with WeComClient(
    corp_id="YOUR_CORP_ID",
    corp_secret="YOUR_CORP_SECRET",
) as client:
    response = client.smartsheet.upload_bytes_and_add_attachment_record(
        docid="DOCID",
        sheet_id="SHEET_ID",
        field_key="ATTACHMENT_FIELD_ID",
        file_name="example.txt",
        file_bytes=b"hello wecom",
        spaceid="SPACEID",
        fatherid="FOLDERID",
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
- 上传与微盘模型：从 `wecom_doc_sdk.models.uploads` 导入
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
