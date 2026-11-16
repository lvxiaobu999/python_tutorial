# 大作业 · 团队任务看板 API（task_board）

> examples/ 的首个工程形态项目：正经包结构（`app/` + `routers/`）、合法模块名、可直接 import。
> 范围严格锁定模块 01–04 已学内容；**测试先行**——`tests/` 里的验收套件就是需求文档的 executable 版。

## 一、这是什么

一个多成员协作的任务看板后端：

- 注册登录（第一个注册的用户自动成为 admin）
- 看板（Board）里建任务（Task），任务有状态机：`todo → doing → done`
- 把任务分配给成员 → 对方收到通知（后台任务）
- 任务的一切动静实时广播到看板的 WebSocket 房间；SSE 可回放活动流水
- 中间件给每个请求编号、计时；CORS 为模块 05 的前端留好了门

**它不是图书 CRUD 的复刻**：多路由工程结构、状态机、房间广播、后台通知，都是新形状。

## 二、快速开始

> 👉 **不知道从哪下手？先看 [GUIDE.md](GUIDE.md)（施工指南）**：按顺序的 11 步施工单 + 每步验证命令。

```bash
cd examples/task_board
uv sync                                  # 建虚拟环境装依赖（M0）
uv run pytest -v                         # 现在跑：26 条全红 = TDD 的起点，正常！
uv run uvicorn app.main:app --reload     # 起服务 → http://127.0.0.1:8000/docs
```

红只会一层层退去：M1 完成后「no such table」消失，M2 后 test_users 变绿……每变绿一批，
就是一块功能被验收。最终态：26 passed。

## 三、里程碑（建议顺序，每步以对应测试文件变绿为验收）

| 里程碑 | 内容 | 参考章节 | 验收测试 |
| -------- | ------ | ---------- | ---------- |
| M0 | `uv sync`、服务能起、/docs 可看 | 00 / 03.1 | — |
| M1 | `models.py` 五张表；`uv add alembic` 并完成首次迁移 | 04.1 | 全套从「no such table」变成业务红 |
| M2 | `security.py` + `deps.py` + 用户路由 + `schemas.py`（User 部分） | 04.2 / 03.3 / 03.4 | test_users.py 全绿 |
| M3 | 看板/任务路由：CRUD、状态机、筛选分页、权限 | 03.2~03.6 / 04.1 | test_tasks.py 全绿 |
| M4 | 中间件：X-Request-ID / X-Process-Time-ms / CORS / /debug | 04.3 | test_middleware.py 全绿 |
| M5 | 后台通知：分配任务 → Notification | 04.4 | test_notifications.py 全绿 |
| M6 | WS 房间广播 + SSE 活动回放 | 04.5 / 02.3 | test_realtime.py 全绿 |
| M7 | 全绿 → 让 Claude 评审 + 记学习笔记 | — | `uv run pytest -v` 全绿 |

## 四、数据模型（5 张表）

| 表 | 字段 | 说明 |
| ---- | ------ | ------ |
| User | id, username(唯一), password_hash, role("admin"\|"member") | 密码只存哈希（04.2） |
| Board | id, name | 任务的「房间」 |
| Task | id, board_id(FK→board.id), title, description, status("todo"\|"doing"\|"done"), assignee_id(可空 FK→user.id) | assignee 为空 = 还没分配 |
| Notification | id, user_id(FK), message | 后台任务写入；message 必须含任务标题 |
| Activity | id, board_id(FK), message | 任务增/改/删时**同步**写入；SSE 回放它 |

外键写法：`Field(foreign_key="board.id")`（表名 = 类名小写）。暂时不需要 relationship()。

## 五、API 规格

### 用户（M2）

| 方法 | 路径 | 鉴权 | 请求 | 成功 | 错误 |
| ------ | ------ | ------ | ------ | ------ | ------ |
| POST | /register | — | json `{username, password}` | 201 `{id, username, role}` | 400 用户名重复 |
| POST | /login | — | **表单** `{username, password}` | 200 `{access_token, token_type:"bearer"}` | 401 |
| GET | /me | Bearer | — | 200 `{id, username, role}` | 401 |

### 看板与任务（M3/M5）

| 方法 | 路径 | 鉴权 | 成功 | 错误 |
| ------ | ------ | ------ | ------ | ------ |
| POST | /boards | Bearer | 201 `{id, name}` | 401 |
| GET | /boards | Bearer | 200 `[{id, name}]` | 401 |
| DELETE | /boards/{id} | Bearer + admin | 204（体为空） | 401 / 403 非 admin / 404 |
| POST | /tasks | Bearer | 201 TaskPublic | 401 / 404 板或被分配人不存在 |
| GET | /tasks | Bearer | 200 `[TaskPublic]`；参数 `board_id`（必）、`status`、`assignee_id`、`skip`、`limit`(默认10) | 401 |
| GET | /tasks/{id} | Bearer | 200 | 404 |
| PATCH | /tasks/{id} | Bearer | 200 TaskPublic | 404；409 状态后退/原地 |
| DELETE | /tasks/{id} | Bearer | 204 | 404 |
| GET | /notifications | Bearer | 200 本人通知，**新→旧** | 401 |

TaskPublic 形状：`{id, board_id, title, description, status, assignee_id}`。

**PATCH 三规则**：① 只改带来的字段（`model_dump(exclude_unset=True)`，03.4 老朋友）；
② status 只能前进 `todo→doing→done`（可跳格），后退或原地 → 409；
③ 改了 assignee → 登记后台通知（`tasks.add_task`，参数传**用户名**和**任务标题**）+ 同步写一条 Activity。

### 实时（M6）

- `WS /ws/boards/{board_id}?token=<jwt>`：token 走查询参数（浏览器 WS 带不了 Authorization 头——工程标准变通）。
  验证失败 → 拒绝接入（close 1008）。接入后，该板任务 create/update/delete 时收到
  `{"event": "task_created"|"task_updated"|"task_deleted", "task_id": ..., "title": ...}`。
- `GET /boards/{board_id}/events/stream`：SSE 回放该板最近 ≤20 条 Activity（时间正序），推完自然结束；
  每条 `data: {...}\n\n`；板不存在 → 404。

### 调试口（M4）

- `GET /debug/request-id`：200 `{"request_id": ...}`——必须与响应头 `X-Request-ID` 一致（request.state 两头对上）。
- 所有响应带 `X-Request-ID` + `X-Process-Time-ms`（404/401 也带——中间件管得宽）。
- CORS 放行 `http://localhost:3000`（模块 05 前端预留）。

## 六、预埋的坑（指路不剧透）

1. **后台任务的 session 所有权**：notify 函数别用请求的 session——响应发完它已不可靠；
   自己 `Session(engine)` 自己关。这是本作业最重要的工程细节。
2. **Activity 同步写、Notification 后台写**：前者要被 SSE 立刻回放，后者用户不必等——
   「同步还是后台」是设计判断，不是随手一放。
3. **WS 的 broadcast 发生在 REST 端点里**：WS 端点只管收编/销户（04.5 的分工）。
4. **select 的链式方法要接住返回值**、**可选查询参数 `= None` 不能省**——04.1 老坑再犯就尴尬了。
5. **Alembic**：ini 保持纯 ASCII、URL 配在 env.py（GBK 老坑）；命令带 `uv run` 前缀。

## 七、加分项（全绿之后再玩）

1. 评论表 Comment(task_id, author_id, content) + 路由 + **自己写测试**（04.6 毕业考试）；
2. 给 Task 加 `priority` 字段并**走 Alembic 迁移**（加列铁律：nullable 或带默认值）；
3. 给 User/Task/Activity 补 created_at 时间戳（提示：datetime 字段的默认值怎么写是个小坑）;
4. 「到期任务扫描」：M5 之外再想想——周期性扫描 BackgroundTasks 干不了（它跟着请求走），
   该用什么？（往 02.5 的 `asyncio` 任务 + lifespan 方向想，算预习。）
5. **async 并发路由**：写一个 `async def` 的 `GET /async/fetch-urls`，用 `httpx.AsyncClient` +
   `asyncio.gather`（02.5 老朋友）并发请求若干 URL，返回各自的耗时——体会「非数据库 IO 才配
   async def」：顺手把 CRUD 路由改成 async def 再查库，对比 /docs 里的响应速度，理解什么叫卡事件循环。

## 八、与 projects/ 的关系

- projects/04 各章 = 单文件教学现场；这里 = 多模块工程实践，模块拆分思想（routers/deps/security）
  就是未来 LangChain 项目的骨架；
- 卡住时先看对应章节笔记（docs/04-fastapi进阶/），再看 projects 源码，最后再问 AI——顺序别反。
