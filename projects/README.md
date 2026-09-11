# projects · 练习代码

这里放各阶段的练习代码与示例，与 `docs/` 里的笔记分离。

## 命名约定

```
projects/<模块编号>-<名字>/
```

例如：

```
projects/00-hello/          # 环境搭建阶段的 Hello World
projects/01-todo-cli/       # Python 基础：待办清单命令行工具
projects/03-book-crud/      # FastAPI 基础：图书 CRUD API
projects/07-rag-app/        # LangChain 进阶：RAG 问答
projects/08-ai-chat/        # 项目实战：全栈 AI 聊天应用
```

## 每个项目内部

用 `uv` 初始化（`uv init`），包含自己的 `pyproject.toml` 与 `uv.lock`，保证依赖独立、可复现。
