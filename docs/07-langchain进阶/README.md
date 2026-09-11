# 模块 07 · LangChain 进阶

> 目标：能构建 RAG 与 Agent，掌握可观测与调试手段。

## 章节清单

| 章节 | 主题 |
|------|------|
| 07.1 Embedding 与向量库 | 文本向量化、Chroma/FAISS/pgvector |
| 07.2 RAG | 文档加载、切分、检索、生成、评估 |
| 07.3 Agents 与工具 | Tool、Function Calling、AgentExecutor |
| 07.4 可观测性 | LangSmith、tracing、调试技巧 |

## 学习要点

- **RAG 是当前 LLM 应用最主流的形态**：检索（Retrieve）+ 增强（Augment）+ 生成（Generate），务必吃透。
- **文档切分**（chunking）质量直接影响检索效果，要理解 chunk 大小与重叠的权衡。
- **Agent 是「让 LLM 自己决定调用什么工具」**：掌握 Tool 定义与 Function Calling。
- **复杂多步/有状态工作流交给 LangGraph**（见模块 08），简单任务用 Agent 即可。
- **调试靠 tracing**：用 LangSmith 或日志看清每一步输入输出，而不是瞎猜。

## 练习方向

跑通「上传文档 → 向量化 → 检索 → 问答」的完整 RAG 应用。

## 笔记文件命名

```
07.2-rag.md
07.3-agents.md
07.4-可观测性.md
...
```
