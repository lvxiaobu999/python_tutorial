"""M4 验收 · 中间件与 CORS（04.3）——中间件管得宽：连 401 响应也要穿过它"""


def test_request_id_and_process_time_headers(client):
    resp = client.get("/boards")  # 故意不带 token：401 响应同样要有这两个头
    assert resp.status_code == 401
    assert resp.headers.get("X-Request-ID")
    assert resp.headers.get("X-Process-Time-ms")


def test_request_id_echoes_state(client):
    """request.state 的两头对上：/debug 读到的 = 响应头里的（04.3 的公开验证口）。"""
    resp = client.get("/debug/request-id")
    assert resp.status_code == 200
    assert resp.json() == {"request_id": resp.headers["X-Request-ID"]}


def test_cors_preflight_allows_configured_origin(client):
    """预检 OPTIONS：白名单内的 Origin 要拿到放行头（04.3 的 CORS 骨架 + /docs 无关）。"""
    resp = client.options(
        "/tasks",
        headers={
            "Origin": "http://localhost:3000",
            "Access-Control-Request-Method": "POST",
        },
    )
    assert resp.headers["access-control-allow-origin"] == "http://localhost:3000"
