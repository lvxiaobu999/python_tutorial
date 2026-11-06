# 模块 04 · FastAPI 进阶 — 练习代码

对应教学大纲见 [docs/04-fastapi进阶](../../docs/04-fastapi进阶/README.md)。

> 目标：掌握数据库、认证、异步任务与部署，能上线生产级 API。
> 路线图验收标准：一个带数据库和登录鉴权的完整 API，能用 Docker 跑起来。
> 前置呼应：模块 03 全部章节是直接地基（模型/依赖/异常/状态码全部复用）；02.5 的 async 解释 WebSocket/SSE；02.7 的 pytest 在 04.6 兑现。

## 运行方式

在 `projects/04-fastapi进阶` 目录下（依赖已通过 `uv add` 装好，换电脑先 `uv sync`）：

```bash
uv run fastapi dev "04.1-数据库集成/01-数据库.py"   # 各章同理，换成对应路径
```

启动后打开 <http://127.0.0.1:8000/docs> 调试。`Ctrl+C` 停止。

## 章节与目录结构

```
04-fastapi进阶/
├── 04.1-数据库集成/        # SQLModel 建模、session 依赖、CRUD、Alembic 概念
├── 04.2-认证与授权/        # bcrypt 哈希、JWT 签发校验、OAuth2、依赖保护路由
├── 04.3-中间件与CORS/      # 自定义中间件、CORSMiddleware、预检请求
├── 04.4-后台任务与队列/    # BackgroundTasks；Celery 概念指南
├── 04.5-websocket与流式/   # WebSocket、SSE 流式响应（为 AI 打字机效果铺路）
└── 04.6-测试与部署/        # pytest + TestClient、Dockerfile、uvicorn/gunicorn
```

（按 docs 大纲的 6 章，全部章节内容已生成。）

## 推荐学习顺序

1. **04.1 数据库**：本模块最大的台阶。SQLModel 是 03.3 BaseModel 的"数据库版"，yield 依赖在这里首次真实上岗。
2. **04.2 认证**：JWT 默写级重点。03.5 的 `fake_token_check` 在这里换成真哈希 + 真签名。
3. **04.3 中间件与 CORS**：相对轻松，前后端联调（模块 05）必备。
4. **04.4 后台任务**：短小实用；Celery 部分先读懂概念，有 Redis 环境再动手。
5. **04.5 流式**：AI 应用的关键——LangChain 流式输出（模块 06/09）就是这个形态。
6. **04.6 测试与部署**：收尾。pytest 兑现 02.7，Docker 没装就先做测试部分。

## 模块综合大作业（模块验收）

**图书管理 API v2**——把模块 03 期末大作业从内存版升级为生产版：

| 要求 | 涉及章节 |
|------|---------|
| 图书数据入库（SQLite + SQLModel），重启不丢 | 04.1 |
| 注册/登录，JWT 鉴权；删书需要管理员身份 | 04.2 |
| 查询接口允许跨域访问（给未来的前端页面放行） | 04.3 |
| 删除图书后异步发通知（BackgroundTasks） | 04.4 |
| pytest 覆盖 200/401/404/422 四种响应 | 04.6 |
| （选做）Dockerfile 打包，一条命令跑起来 | 04.6 |

验收方式：`uv run pytest` 全绿；重启服务后数据还在；没带 token 删书得到 401。

## 依赖说明

`uv add "fastapi[standard]" sqlmodel alembic pyjwt bcrypt python-multipart httpx pytest`

- **pyjwt + bcrypt**：JWT 签发与密码哈希（不用 python-jose/passlib——前者少维护，后者与新版 bcrypt 有兼容坑）
- **python-multipart**：OAuth2 表单登录（`OAuth2PasswordRequestForm`）必需
- **sqlmodel + alembic**：数据库建模与迁移
- 数据库文件（`*.db`）已加入 `.gitignore`，不入库
