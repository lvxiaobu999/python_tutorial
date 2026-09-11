# 模块 03 · FastAPI 基础

> 目标：能写一个带参数校验、数据模型、依赖注入的 REST API。

## 章节清单

| 章节 | 主题 |
|------|------|
| 03.1 快速开始 | 安装、第一个 API、自动文档（/docs、/redoc） |
| 03.2 路由 | 路径参数、查询参数、请求体、APIRouter |
| 03.3 Pydantic 模型 | BaseModel、字段类型与校验、嵌套模型 |
| 03.4 响应模型 | response_model、状态码、Header/Cookie |
| 03.5 依赖注入 | Depends、依赖复用、依赖链 |
| 03.6 错误处理 | HTTPException、自定义异常处理器 |

## 学习要点

- **Pydantic** 是 FastAPI 的核心：数据校验、序列化都靠它，理解 `BaseModel`。
- **依赖注入 `Depends`**：这是 FastAPI 最独特的特性，掌握它就能写出干净、可复用的代码。
- 善用自动文档 `/docs`：边写边用 Swagger UI 验证接口。

## 练习方向

实现一个内存存储的 CRUD（增删改查）接口，比如图书管理 API。

## 笔记文件命名

```
03.1-快速开始.md
03.3-pydantic模型.md
03.5-依赖注入.md
...
```
