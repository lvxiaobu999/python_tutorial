"""M6 · 实时路由——WebSocket 房间广播 + SSE 活动回放（04.5 的工程版）

端点规格：
- WS /ws/boards/{board_id}?token=...
    ⭐ token 走查询参数：浏览器端 WebSocket API 无法自定义 Authorization 头，
    这是工程里的标准变通——用 decode_token 验证，非法 → 拒绝接入（close code 1008）
    接入后加入该 board 的「房间」；任务 create/update/delete 时收到 JSON 事件：
        {"event": "task_created" | "task_updated" | "task_deleted", "task_id": ..., "title": ...}
    保活循环参考 04.5：while True + receive_text + WebSocketDisconnect 销户

- GET /boards/{board_id}/events/stream   SSE（text/event-stream）
    回放该板最近 ≤20 条 Activity（id 降序查出后正序输出），推完自然结束（有限流）
    每条格式：data: {"id": ..., "message": ...}\n\n   ——两个 \n 才是一条消息的终点
    board 不存在 → 404；async 生成器 + StreamingResponse（04.5 演示 2 的骨架）

写法提示：
- 广播发生在 REST 端点里：manager.broadcast(board_id, payload)——
  WS 端点只管收编/销户，发消息的时机在业务动作处（这就是「房间」的意义）；
- SSE 的生成器要自己开 session 查库（它是响应过程中跑的，别依赖请求级依赖注入的传递）。
"""

from fastapi import APIRouter

router = APIRouter(tags=["realtime"])
