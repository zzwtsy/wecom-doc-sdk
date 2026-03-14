# 贡献指南（开发规范）

本文档用于统一企业微信文档 SDK 的基础开发规范，便于后续扩展与协作。

## 开发环境

- Python 版本：3.10（与项目 `pyproject.toml` 对齐）
- 建议使用 `uv` 或虚拟环境（`venv`/`conda`）隔离依赖
- 依赖安装（开发环境）：`uv sync --dev`
- 发布包名为 `wecom-doc-sdk`，Python 导入名为 `wecom_doc_sdk`
- 如使用 VS Code/ty，解释器应绑定到仓库内 `.venv`，建议使用 `${workspaceFolder}\\.venv\\Scripts\\python.exe`

## 目录结构与职责边界

- `src/`：SDK 源码，所有业务代码放在此处
- `references/`：版本化维护的官方文档入口与参考索引
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
- 如果模块内需要保留业务别名 `Field`，则统一使用 `from pydantic import Field as PydanticField`，避免与业务模型命名冲突

## HTTP 规范（httpx）

- 使用 `httpx.Client`/`httpx.AsyncClient` 复用连接，避免频繁创建
- 统一超时策略（例如：连接/读取超时都设定）
- 统一请求封装入口，避免在接口层直接拼接请求细节
- 需要时添加重试策略（可后续扩展，不在本次强制实现）

## 错误处理

- 统一使用 `WeComAPIError` 表示企业微信返回的业务错误，使用 `WeComRequestError` 表示网络、HTTP 状态或响应解析错误
- 业务成功始终以 `errcode == 0` 判断，不依赖 `errmsg` 文案做逻辑判断
- 对外暴露的错误信息应尽量保留：错误码、错误信息、原始响应、底层异常原因（如有）
- SDK 层不吞异常，必要时包装后抛出

## 测试规范

- 使用 `pytest`，测试文件以 `test_*.py` 命名
- 测试目录统一放在 `tests/`
- 新增接口应配套至少 1 个核心路径测试

## Git 流程与提交规范

- 分支命名：`feature/*` 新功能，`fix/*` 缺陷修复，`docs/*` 文档更新
- 提交信息格式：`type: summary`，示例：`feat: add smart table client`，类型可用 `feat`/`fix`/`docs`/`refactor`/`test`/`chore`
- 版本发布：遵循 SemVer（`MAJOR.MINOR.PATCH`），打 tag 时与版本号一致

## 发布前检查

- 确认 `pyproject.toml` 中的 `project.name`、`version`、`description` 与 README 描述一致
- 确认 README 中安装命令使用 `wecom-doc-sdk`，导入示例使用 `wecom_doc_sdk`
- 确认公共导出与 README 示例保持一致
- 发布前至少执行一次完整质量检查：`uv run ruff check .`、`uv run black --check .`、`uv run ty check`、`uv run pytest`
- 发布前至少执行一次本地打包与元数据检查：`uv build`、`uvx twine check dist/*`

## 发布命令（uv）

- 本地构建：`uv build`
- 分发包检查：`uvx twine check dist/*`
- 发布到 TestPyPI：`uv publish --index testpypi`
- 发布到 PyPI：`uv publish`

## 质量检查

- 代码风格：`uv run ruff check .`
- 代码格式：`uv run black --check .`
- 类型检查：`uv run ty check`
- 测试：`uv run pytest`
