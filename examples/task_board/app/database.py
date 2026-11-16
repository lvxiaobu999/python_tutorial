"""数据库基座——04.1 的老三样原样搬进工程形态：engine / get_session / SessionDep。

这份是「样板间」：逻辑已写好（你写过两遍了），但请对照 04.1 逐行能讲出为什么。
验收测试会用 dependency_overrides 把 get_session 整体换角（04.6），本文件零改动。
"""

from pathlib import Path
from typing import Annotated

from fastapi import Depends
from sqlmodel import Session, create_engine

# 相对本文件向上定位：examples/task_board/task_board.db——从哪个目录启动都指向同一个库
DB_PATH = Path(__file__).resolve().parent.parent / "task_board.db"

engine = create_engine(
    f"sqlite:///{DB_PATH}",
    # SQLite 默认禁止跨线程复用连接，而 FastAPI 的 def 路由跑在线程池（04.1 老坑）
    connect_args={"check_same_thread": False},
)


def get_session():
    """yield 依赖：yield 前开会话、之后关会话——路由哪怕抛 404 也保证关闭（04.1）。"""
    with Session(engine) as session:
        yield session


SessionDep = Annotated[Session, Depends(get_session)]
