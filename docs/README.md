# docs · 学习笔记目录

本目录存放学习笔记与教程文档。结构按「模块」分层，每个模块一个子目录。

## 索引

| 目录 | 模块 | 说明 |
|------|------|------|
| [教程大纲.md](./教程大纲.md) | — | 全部模块与章节的总目录（学什么） |
| [学习路线图.md](./学习路线图.md) | — | 学习顺序、时间、里程碑（怎么学） |
| [00-环境搭建/](./00-环境搭建/) | 环境搭建 | uv 建项目/加包、IDE、Git |
| [01-python基础/](./01-python基础/) | Python 基础 | 语法、控制流、数据结构、函数 |
| [02-python进阶/](./02-python进阶/) | Python 进阶 | OOP、类型注解、异步、测试 |
| [03-fastapi基础/](./03-fastapi基础/) | FastAPI 基础 | 路由、Pydantic、依赖注入 |
| [04-fastapi进阶/](./04-fastapi进阶/) | FastAPI 进阶 | 数据库、认证、部署 |
| [05-前端AI应用/](./05-前端AI应用/) | 前端 AI 应用 | Streamlit、前后端交互、流式 |
| [06-langchain基础/](./06-langchain基础/) | LangChain 基础 | Model/Prompt/Chain、LCEL |
| [07-langchain进阶/](./07-langchain进阶/) | LangChain 进阶 | RAG、Agent、可观测性 |
| [08-langgraph/](./08-langgraph/) | LangGraph | 状态图、循环、Checkpoint、多 Agent |
| [09-项目实战/](./09-项目实战/) | 项目实战 | 全栈整合与部署 |

## 笔记规范

- 每篇笔记放对应模块子目录下，文件名用 `<章节号>-<主题>.md`（如 `01.4-函数.md`）。
- 笔记用中文，代码块标注语言，尽量附「运行结果」与「踩坑记录」。
- 可让 AI 按本项目的 `study-note` 技能自动生成规范笔记（见根目录 `.claude/skills/study-note/SKILL.md`）。

## 练习代码

练习代码不放在 docs 里，统一放根目录 `projects/<模块编号>-<名字>/`。
