"""M6 验收 · 实时：WS 房间广播 + SSE 活动回放（04.5）

WS 测试写法说明：开着 websocket_connect 上下文的同时，用同一个 client 发 REST 请求——
TestClient 在进程内串起这一切，REST 端点里的 broadcast 会送达「房间」里的连接。
"""

import pytest
from starlette.websockets import WebSocketDisconnect


def test_ws_board_room_receives_task_events(client, alice, board):
    with client.websocket_connect(f"/ws/boards/{board}?token={alice['token']}") as ws:
        resp = client.post(
            "/tasks",
            json={"board_id": board, "title": "实时推送"},
            headers=alice["headers"],
        )
        assert resp.status_code == 201
        event = ws.receive_json()
        assert event["event"] == "task_created"
        assert event["title"] == "实时推送"
        assert event["task_id"] == resp.json()["id"]


def test_ws_rejects_invalid_token(client, board):
    """非法 token：服务端拒绝接入（浏览器场景里 WebSocket 带不了 Authorization 头，
    token 走查询参数是工程标准变通——验不过就 close）。"""
    with pytest.raises(WebSocketDisconnect):
        with client.websocket_connect(f"/ws/boards/{board}?token=not-a-token"):
            pass


def test_sse_replays_activity_feed(client, alice, board):
    """活动流水同步写（创建时就能查到），SSE 回放最近活动后自然结束（有限流）。"""
    h = alice["headers"]
    client.post("/tasks", json={"board_id": board, "title": "任务甲"}, headers=h)
    client.post("/tasks", json={"board_id": board, "title": "任务乙"}, headers=h)

    resp = client.get(f"/boards/{board}/events/stream")
    assert resp.status_code == 200
    assert "text/event-stream" in resp.headers["content-type"]
    assert "任务甲" in resp.text and "任务乙" in resp.text
    assert resp.text.count("data:") >= 2  # SSE 格式：data: 开头
