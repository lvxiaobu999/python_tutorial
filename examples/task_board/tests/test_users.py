"""M2 验收 · 用户与认证：注册 / 登录 / 身份（04.2 bcrypt + JWT + 依赖链）"""

# 与 conftest._register 用的同一个测试密码（内联一份，避免跨包导入的路径问题）
PW = "pw123456"


def test_first_user_is_admin(alice):
    """业务规则：第一个注册的用户自动成为 admin（bootstrap）。"""
    assert alice["user"]["role"] == "admin"
    assert alice["user"]["username"] == "alice"


def test_user_public_shape_hides_password_hash(alice):
    """UserPublic 白名单（03.4）：注册响应里绝不能出现 password_hash。"""
    assert set(alice["user"].keys()) == {"id", "username", "role"}


def test_second_user_is_member(bob):
    assert bob["user"]["role"] == "member"


def test_register_duplicate_rejected(client, alice):
    resp = client.post("/register", json={"username": "alice", "password": PW})
    assert resp.status_code == 400


def test_login_wrong_password_401(client, alice):
    resp = client.post("/login", data={"username": "alice", "password": "wrong!"})
    assert resp.status_code == 401


def test_me_requires_token(client):
    """没带 token → oauth2_scheme 直接 401（路由函数根本不执行）。"""
    assert client.get("/me").status_code == 401


def test_tampered_token_rejected(client, alice):
    """token 改一个字节 → 签名对不上 → 401（04.2 亲眼看过的那个 401）。"""
    bad = {**alice["headers"], "Authorization": alice["headers"]["Authorization"][:-3] + "xyz"}
    assert client.get("/me", headers=bad).status_code == 401
