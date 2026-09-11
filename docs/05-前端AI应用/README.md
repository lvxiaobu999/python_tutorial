# 模块 05 · 前端 AI 应用

> 目标：能给后端套一个可视化界面，支持流式对话。

## 章节清单

| 章节 | 主题 |
|------|------|
| 05.1 技术选型 | Streamlit / Gradio / Next.js 对比与选择 |
| 05.2 Streamlit 开发 | 组件、状态、会话、布局 |
| 05.3 前后端交互 | 调用 FastAPI、httpx、错误处理 |
| 05.4 流式输出 | SSE、WebSocket、打字机效果 |

## 学习要点

- **选型结论**：学习/原型阶段用 **Streamlit**（纯 Python、上手快），正式产品再考虑 Next.js。
- **Streamlit 的状态**：`st.session_state` 管理会话，`st.chat_message` / `st.chat_input` 做聊天界面。
- **流式输出**：前端用 `st.write_stream`，后端 FastAPI 用 SSE 逐 token 返回，是 AI 应用的核心体验。

## 练习方向

做一个能对话的界面：前端 Streamlit，后端调 FastAPI 的流式接口。

## 笔记文件命名

```
05.1-技术选型.md
05.2-streamlit开发.md
05.4-流式输出.md
...
```
