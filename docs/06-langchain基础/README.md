# 模块 06 · LangChain 基础

> 目标：理解 LLM 应用的核心抽象，能写简单对话/链式调用。

## 章节清单

| 章节 | 主题 |
|------|------|
| 06.1 核心概念 | LangChain 定位、Model/Prompt/Chain 抽象 |
| 06.2 Chat Models | 接入 LLM（OpenAI/Claude/本地）、消息类型 |
| 06.3 Prompt 模板 | PromptTemplate、ChatPromptTemplate、Few-shot |
| 06.4 输出解析器 | OutputParser、结构化输出、PydanticOutputParser |
| 06.5 Chains | LCEL（| 管道）、RunnableSequence |
| 06.6 记忆 | ConversationBufferMemory、历史管理 |

## 学习要点

- **LCEL 是核心语法**：`prompt | model | parser` 的管道写法，是 LangChain 现代用法的基础。
- **消息类型**：理解 `SystemMessage` / `HumanMessage` / `AIMessage` 的区别。
- **结构化输出**：让 LLM 返回可编程处理的 JSON，是连接「LLM」与「后端逻辑」的关键。

## 练习方向

写一个带记忆的对话脚本；让 LLM 按 Pydantic 模型返回结构化结果。

## 笔记文件命名

```
06.1-核心概念.md
06.5-lcel.md
06.6-记忆.md
...
```
