"""组装车间：app 实例 + 建表 + 挂路由 + （M4 由你注册的）中间件。

工程形态和 04 章单文件练习的最大不同：这里只做「组装」，
每个端点的实现都在 routers/ 下各自的模块里（03.2 APIRouter 的正式上岗）。

运行：
    uv run uvicorn app.main:app --reload    → http://127.0.0.1:8000/docs
"""

from fastapi import FastAPI
from sqlmodel import SQLModel

from app import models  # noqa: F401  导入即注册全部表模型——没有这行 create_all 是空转
from app.database import engine
from app.routers import boards, realtime, tasks, users

# 建表：04.1 的老做法（只补建不存在的表；改表结构是 Alembic 的活——M1 里程碑你会正式走一遍）
SQLModel.metadata.create_all(engine)

app = FastAPI(title="大作业 · 团队任务看板 API")

app.include_router(users.router)
app.include_router(boards.router)
app.include_router(tasks.router)
app.include_router(realtime.router)


# ============ M4 · 中间件与 CORS（04.3 的工程版，全部由你实现） ============
# 需要实现三件事（实现代码建议放本文件底部，对照 04.3 逐条能讲出原理）：
#
# 1. 请求中间件 add_request_context：
#    - 入向生成 request_id（uuid4），存进 request.state.request_id；
#    - 出向写响应头 X-Request-ID 和 X-Process-Time-ms（毫秒，一位小数）；
#    - call_next 的类型标注在「源头」（04.3：类型标进签名，Pylance 全程推断，不需要 cast）。
#
# 2. GET /debug/request-id 端点：返回 {"request_id": request.state.request_id}
#    ——验收测试会断言它与响应头 X-Request-ID 一致（04.3「两头对上」的公开验证口）。
#
# 3. CORS：放行 http://localhost:3000（allow_origins / allow_methods=["*"] / allow_headers=["*"]）
#    ——模块 05 的前端开发服务器就长这个地址。注意注册顺序 = 洋葱层次（后注册在最外层）。
#
# 验收：tests/test_middleware.py 三条测试。
