"""验收测试的基础设施——04.6 那套内存库方案的正式上岗（本文件是给你的样板，不用改）。

三个设计要点（全是学过的）：
1. 每个测试一台「进程内客户端」+ 一个全新的内存 SQLite——状态隔离是天然的，
   不需要 04 章那种 reset_books()；
2. dependency_overrides 把 get_session 整体换角成测试 session，业务代码零改动；
3. TestClient 会等 BackgroundTasks 跑完才返回（04.4 的坑），所以「分配任务 → 通知落库」
   在测试里是同步可见的，断言确定性强。

运行（在 examples/task_board 目录下）：
    uv run pytest -v        # 全绿 = 大作业验收通过
"""

import pytest
from fastapi.testclient import TestClient
from sqlalchemy.pool import StaticPool
from sqlmodel import Session, SQLModel, create_engine

from app import models  # noqa: F401  导入即注册表模型（M1 完成前注册不到东西）
from app.database import get_session
from app.main import app

PW = "pw123456"  # 测试账号的统一密码


@pytest.fixture()
def client():
    """每个测试一台进程内客户端 + 一个活不过本测试的内存库。"""
    engine = create_engine(
        "sqlite:///:memory:",
        connect_args={"check_same_thread": False},  # def 路由跑在线程池（04.1 老坑）
        poolclass=StaticPool,  # 内存库每条连接各开一个空库，必须共用（04.6 老坑）
    )
    SQLModel.metadata.create_all(engine)

    def get_test_session():
        with Session(engine) as session:
            yield session

    app.dependency_overrides[get_session] = get_test_session
    with TestClient(app) as c:
        yield c
    app.dependency_overrides.clear()


# ---------- 人与板的fixture：测试只声明，pytest 自动递进来（02.7 / 04.6） ----------
def _register(client: TestClient, username: str) -> dict:
    resp = client.post("/register", json={"username": username, "password": PW})
    assert resp.status_code == 201, f"注册失败：{resp.text}"
    token = client.post(
        "/login", data={"username": username, "password": PW}
    ).json()["access_token"]
    return {
        "user": resp.json(),  # {"id", "username", "role"}——UserPublic 的形状
        "token": token,
        "headers": {"Authorization": f"Bearer {token}"},
    }


@pytest.fixture()
def alice(client):
    """第一个注册的用户——按业务规则自动成为 admin。"""
    return _register(client, "alice")


@pytest.fixture()
def bob(alice, client):
    """第二个用户——member。依赖 alice 是刻意的：保证注册顺序。"""
    return _register(client, "bob")


@pytest.fixture()
def board(client, alice):
    """一块已建好的看板，返回 board_id。"""
    resp = client.post(
        "/boards", json={"name": "开发计划"}, headers=alice["headers"]
    )
    assert resp.status_code == 201, resp.text
    return resp.json()["id"]
