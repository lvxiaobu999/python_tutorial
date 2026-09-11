# 模块 08 · LangGraph

> 目标：能构建可循环、带状态、可人工干预的复杂 Agent 工作流。

## 章节清单

| 章节 | 主题 |
|------|------|
| 08.1 核心概念 | 图 vs 链、State/Node/Edge 三大抽象、何时用 LangGraph |
| 08.2 StateGraph 基础 | 定义 State（TypedDict）、节点函数、add_node/add_edge、compile、invoke/stream |
| 08.3 循环与分支 | add_conditional_edges、条件路由、循环（相对 Chain 的核心优势） |
| 08.4 Checkpoint 与持久化 | checkpointer、MemorySaver、断点续跑、thread_id 状态持久化 |
| 08.5 Human-in-the-loop | interrupt、人工审批/干预节点 |
| 08.6 多 Agent 与复杂工作流 | 多智能体协作、Supervisor 模式、与 FastAPI 的流式集成 |

## 学习要点

- **图 vs 链**：Chain 是线性的，LangGraph 用「图」表达任意控制流——这是它取代旧 Chain API 的根本原因。
- **State 是灵魂**：整个图共享一个 `State`（通常用 `TypedDict` 定义），节点读写它，边决定流向。
- **循环靠条件边**：`add_conditional_edges` 让流程能回头重跑，是「Agent 反复试错」的实现基础。
- **Checkpoint**：`checkpointer` 让每次状态落盘，配合 `thread_id` 实现断点续跑和多会话隔离。
- **多 Agent**：复杂任务拆给多个 Agent，用 Supervisor 或消息传递协调。

## 练习方向

跑通一个「带人工审批步骤的多步 Agent 工作流」；再把它接到 FastAPI 接口里做流式返回。

## 笔记文件命名

```
08.1-核心概念.md
08.2-stategraph.md
08.3-循环与分支.md
08.4-checkpoint.md
08.6-多agent.md
...
```
