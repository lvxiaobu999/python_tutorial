"""M3/M5 · 任务路由——CRUD + 状态机 + 筛选分页 + 分配通知（本作业的主战场）

端点规格（详细字段/错误码见 README「API 规格」节）：
- POST /tasks             201 → TaskPublic；board_id 或 assignee_id 不存在 → 404
- GET /tasks              200 → [TaskPublic]；查询参数：board_id（必）、status、assignee_id、skip、limit（默认 10）
                          过滤和翻页是数据库挑行：where/offset/limit（04.1），不是拉全表回 Python 切
- GET /tasks/{id}         200 / 404
- PATCH /tasks/{id}       200 → TaskPublic；规则三条：
                          ① 只改带来的字段（exclude_unset，03.4）；
                          ② status 只能前进 todo→doing→done（可跳格），后退或原地 → 409「状态只能前进」；
                          ③ 改了 assignee_id → 触发后台通知（M5：tasks.add_task，04.4）+ 同步写一条 Activity
- DELETE /tasks/{id}      204 / 404

⭐ 同步与后台的分工（本作业的核心设计判断）：
- Activity（活动流水）同步写——SSE 回放要立刻能查到；
- Notification（通知）后台写——用户不用等它落库（04.4：先回话，再干活）。
"""

from fastapi import APIRouter

router = APIRouter(tags=["tasks"])
