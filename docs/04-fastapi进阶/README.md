# 模块 04 · FastAPI 进阶

> 目标：掌握数据库、认证、异步任务与部署，能上线生产级 API。

## 章节清单

| 章节 | 主题 |
|------|------|
| 04.1 数据库集成 | SQLAlchemy / SQLModel、迁移（Alembic） |
| 04.2 认证与授权 | JWT、OAuth2、密码哈希、依赖保护路由 |
| 04.3 中间件与 CORS | 自定义中间件、跨域配置 |
| 04.4 后台任务与队列 | BackgroundTasks、Celery/RQ |
| 04.5 WebSocket 与流式 | WebSocket、SSE 流式响应 |
| 04.6 测试与部署 | TestClient、pytest、Docker、Uvicorn/Gunicorn |

## 学习要点

- **数据库**：SQLModel 是 FastAPI 官方推荐，与 Pydantic 无缝；Alembic 管迁移。
- **认证**：JWT 的签发/校验流程要能默写，密码必须哈希（passlib/bcrypt）。
- **流式响应**是 AI 应用的关键：SSE/WebSocket 为 LangChain 流式输出铺路。

## 练习方向

把模块 03 的 CRUD 换成真数据库，加上登录鉴权，最后 Docker 化部署。

## 笔记文件命名

```
04.1-数据库集成.md
04.2-认证与授权.md
04.5-websocket与流式.md
...
```
