"""M5 验收 · 后台通知：分配任务 → 被分配人收到通知（04.4 + TestClient 会等任务）"""


def test_assigning_notifies_assignee(client, alice, bob, board):
    task_id = client.post(
        "/tasks",
        json={"board_id": board, "title": "修登录页", "assignee_id": bob["user"]["id"]},
        headers=alice["headers"],
    ).json()["id"]

    resp = client.get("/notifications", headers=bob["headers"])
    assert resp.status_code == 200
    notifications = resp.json()
    assert any("修登录页" in n["message"] for n in notifications)  # 通知里必须带任务标题
    assert all(n["user_id"] == bob["user"]["id"] for n in notifications)

    # 分配只通知被分配人：alice 自己的信箱是空的
    assert client.get("/notifications", headers=alice["headers"]).json() == []


def test_notifications_isolated_per_user(client, alice, bob, board):
    """两次分配 → bob 收到两条，且新的在前（id 降序）。"""
    h = alice["headers"]
    client.post("/tasks", json={"board_id": board, "title": "任务一", "assignee_id": bob["user"]["id"]}, headers=h)
    client.post("/tasks", json={"board_id": board, "title": "任务二", "assignee_id": bob["user"]["id"]}, headers=h)

    notifications = client.get("/notifications", headers=bob["headers"]).json()
    assert len(notifications) == 2
    assert "任务二" in notifications[0]["message"]  # 新→旧
    assert "任务一" in notifications[1]["message"]


def test_notifications_require_auth(client):
    assert client.get("/notifications").status_code == 401
