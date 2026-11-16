# 施工指南 · 从 26 红 到 26 绿

> README 是「需求与规格」（查表用），本文件是「按什么顺序干、每步怎么验证」（动手时开着）。
> 所有时间只是参考——卡住是正常的，卡壳处理见文末。

## 0. 先建立全局感（10 分钟）

这个工程只有 4 层，数据流单向：

```text
请求 → main.py（组装/中间件）→ routers/（端点）→ deps.py（守门）→ models/schemas（数据形状）→ database.py（库）
```

9 个文件标了 TODO，没有一个是新知识——都是 04 章写过的东西，只是搬进工程结构、按新业务组装：

| 文件 | 你要做什么 | 对应章节 | 变绿的测试 |
| ------ | ------ | ------ | ------ |
| `app/models.py` | 定义 5 张表 | 04.1 | 全套不再报 no such table |
| `app/schemas.py` | 请求/响应模型 | 03.3 / 03.4 | 被各测试间接验收 |
| `app/security.py` | 哈希 + JWT 四函数 | 04.2 | test_users |
| `app/deps.py` | 守门员依赖链 | 04.2 | test_users |
| `app/routers/users.py` | 注册/登录/me 三端点 | 04.2 | test_users |
| `app/routers/boards.py` | 看板三端点 | 03.2 | test_tasks 里 delete_board 那条 |
| `app/routers/tasks.py` | 任务 CRUD + 状态机（主战场） | 03 全家 + 04.1 | test_tasks |
| `app/main.py` 中间件区 | 编号/计时/CORS | 04.3 | test_middleware |
| `app/background.py` + tasks.py 登记处 | 分配通知 | 04.4 | test_notifications |
| `app/ws.py` + `app/routers/realtime.py` | 房间广播 + SSE | 04.5 | test_realtime |

唯一给全的文件是 `database.py`（样板间，要能逐行讲出为什么）和 `tests/conftest.py`（测试基建）。

## 施工单（按顺序打勾）

### ✅ 第 1 步 · M1 建表（约 30 分钟）

打开 `app/models.py`，写 5 个 `table=True` 的类。字段清单照 README 第四节的表，一个类一个类来：

- 5 个类：`User` / `Board` / `Task` / `Notification` / `Activity`
- 每张表第一个字段都是 `id: int | None = Field(default=None, primary_key=True)`
- 外键写法：`Field(foreign_key="board.id")`——引号里是**表名.字段**（表名 = 类名小写）
- `Task.assignee_id` 是可空外键：`int | None = Field(default=None, foreign_key=...)`

验证形状对了：

```bash
uv run python -c "from app import models; from sqlmodel import SQLModel; print(list(SQLModel.metadata.tables))"
# 打印出 5 个表名 = 通过
```

然后走一遍迁移（去年在 04.1 是我带着走的，这次你自己来）：`uv add alembic` →
`uv run alembic init migrations` → `env.py` 里配数据库 URL（**ini 保持纯 ASCII**，URL 写 env.py）
→ `uv run alembic revision --autogenerate -m "init tables"` → `uv run alembic upgrade head`。

### ✅ 第 2 步 · M2-a 用户模型（约 10 分钟）

`app/schemas.py` 先写 `RegisterIn`、`UserPublic` 两个模型。
UserPublic 只有 `id / username / role` 三个字段——**password_hash 绝不出现**（03.4 白名单）。

### ✅ 第 3 步 · M2-b 密码与令牌（约 30 分钟）

`app/security.py` 四个函数：`hash_password` / `verify_password` / `create_token` / `decode_token`。
建议**先合上 04.2 源码凭记忆写，再对照订正**——这章你踩过真实的坑（sub 写死导致全员 401）。

- `exp` 用 `config.py` 里的 `ACCESS_TOKEN_EXPIRE_SECONDS`，别再硬编码
- `decode_token` 验签失败/过期时向上抛异常，让调用方（deps.py）决定怎么拒绝

### ✅ 第 4 步 · M2-c 守门员（约 20 分钟）

`app/deps.py`：实现 `get_current_user`（decode → 查库 → 401/返回用户）和 `require_admin`，
然后在文件末尾定义两个 Annotated 别名：`CurrentUser` / `AdminUser`（给路由用）。

### ✅ 第 5 步 · M2-d 用户路由（约 40 分钟）

`app/routers/users.py` 三端点：POST /register（201、重复 400、**第一个注册的用户自动 admin**）、
POST /login（表单！`OAuth2PasswordRequestForm`）、GET /me。

验证：

```bash
uv run pytest tests/test_users.py -v    # 目标：7 passed
```

### ✅ 第 6 步 · M3-a 看板路由（约 20 分钟）

`app/routers/boards.py` 三端点——全作业最简单的路由，拿来练 APIRouter 手感。
DELETE /boards 用 `AdminUser` 依赖（require_admin 第一个上岗现场）。

### ✅ 第 7 步 · M3-b 任务路由（约 2 小时，主战场，拆四小口吃）

`app/routers/tasks.py`，**一口一口吃，每口跑一次测试看红条减少**：

1. POST /tasks + GET /tasks/{id}（含板不存在 404、被分配人不存在 404）
2. PATCH（三规则：`exclude_unset` 只改带来的字段；status 只前进可跳格否则 409；改 assignee 先记账）
3. DELETE /tasks/{id}（204 / 404）
4. GET /tasks 列表（`board_id` 必填查询参数 + `status` / `assignee_id` 筛选 + `skip` / `limit` 翻页——全部数据库挑行）

```bash
uv run pytest tests/test_tasks.py -v    # 目标：10 passed
```

### ✅ 第 8 步 · M4 中间件（约 40 分钟）

`app/main.py` 底部 TODO 区：一个请求中间件（入向 `request.state` 存 request_id，出向写两个响应头）
+ GET /debug/request-id 端点 + CORS 放行 `http://localhost:3000`。

```bash
uv run pytest tests/test_middleware.py -v    # 目标：3 passed
```

### ✅ 第 9 步 · M5 后台通知（约 30 分钟）

`app/background.py` 的 `notify_assignment`：⚠️ **自己开 Session(engine)，别用请求的 session**
（README 预埋坑第 1 条，这是全作业最重要的工程细节）。然后在 tasks.py 的 PATCH 里
`tasks.add_task(...)` 登记——传函数本身 + 参数。

```bash
uv run pytest tests/test_notifications.py -v    # 目标：3 passed
```

### ✅ 第 10 步 · M6 实时（约 1.5 小时，也是四小口）

1. `app/ws.py`：多房间 manager（04.5 的 `list` 升级成 `dict[int, list[WebSocket]]`）
2. `app/routers/realtime.py` 的 WS 端点：`?token=` 查询参数 → `decode_token` →
   验不过 `close(code=1008)`；验过 → `manager.connect`，循环收发保活
3. `tasks.py` 的 create/patch/delete 里各加两行：**同步写一条 Activity** + `manager.broadcast(...)`
   ——事件 payload 的键名照 `tests/test_realtime.py` 里断言的写（测试即需求）
4. SSE 端点：async 生成器回放该板最近 ≤20 条 Activity（有限流，推完结束）

```bash
uv run pytest tests/test_realtime.py -v    # 目标：3 passed
```

### ✅ 第 11 步 · 收官（约 30 分钟）

```bash
uv run pytest -v    # 26 passed = 毕业
```

之后：让 Claude 评审代码 + 记学习笔记，再考虑 README 第七节的加分项。

## 通用方法论

- **测试即需求**：规格看不懂时，直接读对应测试文件——断言就是行为的权威定义；
- **红绿节奏**：一次只追求一批测试变绿，别想一口气写完再调；
- **/docs 是手工验收场**：每完成一个路由就 `uv run uvicorn app.main:app --reload` 点一点，
  亲眼看过比只看测试绿更有体感（Authorize 按钮 M2 后就能用了）；
- **卡壳三层**（顺序别反）：`docs/04-fastapi进阶/` 笔记 → `projects/04-fastapi进阶/` 源码 →
  把**报错原文**贴给 AI。跳过前两层直接问 AI = 放弃这次复习机会；
- **每个路由动手前先做一次 def / async def 判断**（这是 FastAPI 里 async 的核心决策）：
  同步数据库调用 → `def`（线程池兜底，别卡事件循环——04.4 反例）；非数据库 IO（调外部 HTTP、
  模型流式）→ `async def`。本项目的 CRUD 刻意用 `def`，async 出现在中间件 / WS / SSE 三处
  不可绕开的地方；async 的大规模实战在模块 06+（LangChain 的 ainvoke / astream 全是 async）。
