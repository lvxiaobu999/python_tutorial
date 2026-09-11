# 模块 09 · 项目实战

> 目标：把以上技能串成一个完整的 AI 应用并部署。

## 章节清单

| 章节 | 主题 |
|------|------|
| 09.1 需求与架构 | 项目设计、技术选型、目录结构 |
| 09.2 后端实现 | FastAPI + LangChain/LangGraph + 数据库 |
| 09.3 前端实现 | Streamlit / Next.js 对接 |
| 09.4 部署上线 | Docker 化、云部署、监控 |

## 建议项目选题

1. **个人知识库问答**（RAG + LangGraph）：上传自己的笔记/文档，做私有问答。
2. **AI 聊天助手**：多轮对话 + 工具调用 + 流式输出，用 LangGraph 编排多步工作流。
3. **文档总结/翻译工具**：上传文档，输出结构化总结。

## 学习要点

- **架构先行**：画清楚「前端 → FastAPI → LangChain/LangGraph → 模型/向量库」的数据流再动手。
- **分层组织代码**：routers / models / services / schemas 分层，别全堆在一个文件。
- **部署**：Docker 化前后端，用 `uv.lock` 保证依赖一致，注意 API key 用环境变量管理。

## 项目目录建议

```
projects/09-<项目名>/
├── backend/            # FastAPI + LangChain/LangGraph
│   ├── app/
│   │   ├── main.py
│   │   ├── routers/
│   │   ├── models/
│   │   ├── schemas/
│   │   └── services/
│   ├── pyproject.toml
│   └── Dockerfile
├── frontend/           # Streamlit 或 Next.js
└── README.md
```

## 笔记文件命名

```
09.1-需求与架构.md
09.2-后端实现.md
09.4-部署上线.md
...
```
