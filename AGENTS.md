# Agent Guide

本文件用于统一协作式代码生成/修改的约定，帮助快速上手本仓库。

## 项目概览

- 项目：企业微信文档 SDK（Python）
- 目标：封装企业微信文档相关 API（当前已覆盖智能表格内容、文档权限、文档管理、文档内容，并持续扩展）
- 技术栈：`httpx` + `pydantic` + 完整类型标注
- 发布包名：`wecom-doc-sdk`
- Python 导入名：`wecom_doc_sdk`

## 目录与结构

- `src/`：SDK 源码（使用 `src` 布局）
- `references/`：版本化维护的官方文档入口与参考索引
- `docs/`：企业微信接口文档参考
- `tests/`：pytest 测试（如不存在，新增时遵循该目录）

建议包结构（新增代码优先遵循）：  
`src/wecom_doc_sdk/`  
`src/wecom_doc_sdk/client.py`（HTTP 客户端封装）  
`src/wecom_doc_sdk/models/`（Pydantic 模型）  
`src/wecom_doc_sdk/apis/`（接口封装）

## 开发规范要点

- 中文注释：关键逻辑、边界条件与业务语义必须有中文说明
- 类型标注：函数/方法需完整类型标注，公开接口必须明确输入输出
- HTTP：使用 `httpx.Client/AsyncClient` 复用连接；统一超时与错误处理
- Pydantic：v2 写法；序列化用 `model_dump()`，校验用 `model_validate()`
- Pydantic 命名冲突：若模块内需要保留业务别名 `Field`，统一将 Pydantic 的 `Field` 导入为 `PydanticField`
- 字段文档：公开请求/响应模型字段应提供 `Field(description="...")`，用于 IDE 悬停与文档生成
- 约束落地：文档中的“二选一/互斥/至少一项/条件必填”需通过 `model_validator` 等方式显式校验
- 枚举规范：默认使用简单 `Enum/IntEnum` 成员值，不使用 `label` 扩展字段；语义说明优先放在类 docstring（不依赖尾行注释）
- 错误处理：统一沿用 `WeComAPIError` / `WeComRequestError`，并以 `errcode == 0` 作为业务成功判断标准
- 扩展性：新增接口按模块拆分，避免把逻辑堆在单文件
- 导出约束：根包 `wecom_doc_sdk` 保持精简，只导出客户端等入口对象；异常与请求/响应模型分别从对应子模块导入

详细规范见 `CONTRIBUTING.md`。

## 常用命令

- 安装依赖（开发）：`uv sync --dev`
- IDE/ty 解释器：优先使用仓库内 `.venv`，VS Code 建议绑定 `${workspaceFolder}\\.venv\\Scripts\\python.exe`
- 代码风格：`uv run ruff check .`
- 代码格式：`uv run black --check .`
- 类型检查：`uv run ty check`
- 测试：`uv run pytest`
- 本地构建：`uv build`
- 分发包检查：`uvx twine check dist/*`

## 变更约定

- 尽量小步提交，改动保持聚焦
- 不随意重排/重写与本次任务无关的代码
- 修改公共接口需同步补充类型与文档
- 涉及发布相关改动时，同步检查 `pyproject.toml`、README 安装命令、导入示例与公共导出是否一致
