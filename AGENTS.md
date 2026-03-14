# Agent Guide

本文件用于统一协作式代码生成/修改的约定，帮助快速上手本仓库。

## 项目概览

- 项目：企业微信文档 SDK（Python）
- 目标：封装企业微信文档相关 API（当前聚焦“管理智能表格内容”）
- 技术栈：`httpx` + `pydantic` + 完整类型标注

## 目录与结构

- `src/`：SDK 源码（使用 `src` 布局）
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
- 扩展性：新增接口按模块拆分，避免把逻辑堆在单文件

详细规范见 `CONTRIBUTING.md`。

## 常用命令

- 安装依赖（开发）：`pip install -e .[dev]` 或 `uv pip install -e .[dev]`
- 代码风格：`ruff check .`
- 代码格式：`black --check .`
- 测试：`pytest`

## 变更约定

- 尽量小步提交，改动保持聚焦
- 不随意重排/重写与本次任务无关的代码
- 修改公共接口需同步补充类型与文档
