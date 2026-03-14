# 贡献指南（开发规范）

本文档用于统一企业微信文档 SDK 的基础开发规范，便于后续扩展与协作。

## 开发环境

- Python 版本：3.10（与项目 `pyproject.toml` 对齐）
- 建议使用 `uv` 或虚拟环境（`venv`/`conda`）隔离依赖
- 依赖安装（开发环境）：`uv pip install -e .[dev]` 或 `pip install -e .[dev]`

## 目录结构与职责边界

- `src/`：SDK 源码，所有业务代码放在此处
- `docs/`：企业微信文档与接口说明，仅作参考
- `tests/`：单元测试目录（如不存在，新增时保持该结构）
- 建议包结构示例：`src/wecom_doc_sdk/`、`src/wecom_doc_sdk/client.py`、`src/wecom_doc_sdk/models/`、`src/wecom_doc_sdk/apis/`
- 扩展约束：新增接口优先在 `apis/` 下增量扩展，避免接口逻辑堆在单一文件中

## 代码风格

- 命名：类用 `PascalCase`，函数/变量用 `snake_case`，常量用 `UPPER_SNAKE_CASE`
- 导入顺序：标准库 > 第三方库 > 本地模块，使用 `ruff` 自动整理
- 中文注释：关键逻辑、边界条件与业务语义需配中文注释
- Docstring：公开 API（对外可调用的函数/类）必须写简短 docstring

## 类型规范

- 所有函数与方法需要完整类型标注
- 公开接口必须明确输入与返回类型
- 优先使用 `typing` 中的显式类型（如 `Sequence`、`Mapping`）

## Pydantic 规范（v2）

- 模型统一继承 `pydantic.BaseModel`
- 字段别名、默认值、描述使用 `Field`
- 序列化/反序列化：输出用 `model_dump()`，输入用 `model_validate()`

## HTTP 规范（httpx）

- 使用 `httpx.Client`/`httpx.AsyncClient` 复用连接，避免频繁创建
- 统一超时策略（例如：连接/读取超时都设定）
- 统一请求封装入口，避免在接口层直接拼接请求细节
- 需要时添加重试策略（可后续扩展，不在本次强制实现）

## 错误处理

- 统一错误类型（建议自定义 `WeComDocError` 等基类）
- 对外暴露的错误信息应包含：错误码、错误信息、原始响应（如有）
- SDK 层不吞异常，必要时包装后抛出

## 测试规范

- 使用 `pytest`，测试文件以 `test_*.py` 命名
- 测试目录统一放在 `tests/`
- 新增接口应配套至少 1 个核心路径测试

## Git 流程与提交规范

- 分支命名：`feature/*` 新功能，`fix/*` 缺陷修复，`docs/*` 文档更新
- 提交信息格式：`type: summary`，示例：`feat: add smart table client`，类型可用 `feat`/`fix`/`docs`/`refactor`/`test`/`chore`
- 版本发布：遵循 SemVer（`MAJOR.MINOR.PATCH`），打 tag 时与版本号一致

## 质量检查

- 代码风格：`ruff check .`
- 代码格式：`black --check .`
- 测试：`pytest`
