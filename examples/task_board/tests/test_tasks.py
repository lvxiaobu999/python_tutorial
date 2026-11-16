"""M3 验收 · 任务 CRUD / 筛选分页 / 状态机 / 权限"""


def test_create_task_defaults(client, alice, board):
    resp = client.post(
        "/tasks", json={"board_id": board, "title": "搭骨架"}, headers=alice["headers"]
    )
    assert resp.status_code == 201, resp.text
    body = resp.json()
    assert body["status"] == "todo"  # 新任务默认 todo
    assert body["title"] == "搭骨架"
    assert body["assignee_id"] is None  # 「还没分配」是正常状态
    assert "id" in body and "board_id" in body


def test_board_must_exist_404(client, alice):
    resp = client.post(
        "/tasks", json={"board_id": 999, "title": "幽灵任务"}, headers=alice["headers"]
    )
    assert resp.status_code == 404


def test_assignee_must_exist_404(client, alice, board):
    resp = client.post(
        "/tasks",
        json={"board_id": board, "title": "无主任务", "assignee_id": 999},
        headers=alice["headers"],
    )
    assert resp.status_code == 404


def test_get_missing_task_404(client, alice):
    resp = client.get("/tasks/999", headers=alice["headers"])
    assert resp.status_code == 404


def test_patch_updates_only_sent_fields(client, alice, board):
    task_id = client.post(
        "/tasks",
        json={"board_id": board, "title": "原标题", "description": "原描述"},
        headers=alice["headers"],
    ).json()["id"]

    resp = client.patch(
        f"/tasks/{task_id}", json={"title": "新标题"}, headers=alice["headers"]
    )
    assert resp.status_code == 200
    body = resp.json()
    assert body["title"] == "新标题"
    assert body["description"] == "原描述"  # 没带的字段原封不动（exclude_unset）


def test_status_machine_forward_only(client, alice, board):
    """状态机：todo→doing→done 可走，可跳格，不可后退、不可原地。"""
    task_id = client.post(
        "/tasks", json={"board_id": board, "title": "状态实验"}, headers=alice["headers"]
    ).json()["id"]
    h = alice["headers"]

    assert client.patch(f"/tasks/{task_id}", json={"status": "done"}, headers=h).status_code == 200  # 允许跳格

    assert client.patch(f"/tasks/{task_id}", json={"status": "doing"}, headers=h).status_code == 409  # 后退
    assert client.patch(f"/tasks/{task_id}", json={"status": "done"}, headers=h).status_code == 409  # 原地

    assert client.get(f"/tasks/{task_id}", headers=h).json()["status"] == "done"  # 失败的补丁不生效


def test_pagination_and_filter(client, alice, bob, board):
    """筛选与翻页：数据库挑行（where/offset/limit），不是拉回 Python 切片。"""
    h = alice["headers"]
    ids = [
        client.post("/tasks", json={"board_id": board, "title": f"任务{i}"}, headers=h).json()["id"]
        for i in (1, 2, 3)
    ]
    client.patch(f"/tasks/{ids[0]}", json={"assignee_id": bob["user"]["id"]}, headers=h)

    resp = client.get("/tasks", params={"board_id": board}, headers=h)
    assert resp.status_code == 200
    assert len(resp.json()) == 3

    resp = client.get("/tasks", params={"board_id": board, "limit": 2}, headers=h)
    assert [t["id"] for t in resp.json()] == ids[:2]  # 按创建顺序

    resp = client.get("/tasks", params={"board_id": board, "skip": 1, "limit": 2}, headers=h)
    assert [t["id"] for t in resp.json()] == ids[1:]

    resp = client.get("/tasks", params={"board_id": board, "assignee_id": bob["user"]["id"]}, headers=h)
    assert [t["id"] for t in resp.json()] == [ids[0]]

    resp = client.get("/tasks", params={"board_id": board, "status": "todo"}, headers=h)
    assert len(resp.json()) == 3


def test_delete_task_204(client, alice, board):
    task_id = client.post(
        "/tasks", json={"board_id": board, "title": "短命任务"}, headers=alice["headers"]
    ).json()["id"]
    assert client.delete(f"/tasks/{task_id}", headers=alice["headers"]).status_code == 204
    assert client.get(f"/tasks/{task_id}", headers=alice["headers"]).status_code == 404


def test_tasks_require_auth(client, board):
    assert client.post("/tasks", json={"board_id": board, "title": "匿名"}).status_code == 401
    assert client.get("/tasks", params={"board_id": board}).status_code == 401


def test_delete_board_admin_only(client, alice, bob, board):
    """require_admin 的自然落点：member → 403，admin → 204。"""
    resp = client.delete(f"/boards/{board}", headers=bob["headers"])
    assert resp.status_code == 403

    resp = client.delete(f"/boards/{board}", headers=alice["headers"])
    assert resp.status_code == 204
    assert resp.content == b""  # 204 的语义：响应体必须为空
