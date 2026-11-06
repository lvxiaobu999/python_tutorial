"""04.1 数据库集成：让数据真正存下来

前 03 章的图书都活在 Python 变量里——服务一重启就清零。
本章引入 SQLModel（Pydantic + SQLAlchemy 的合体）：用「定义类」的方式定义表，
用「操作对象」的方式读写数据库；03.5 的 yield 依赖也迎来第一个真实用例。

运行（在 projects/04-fastapi进阶 目录下）：
    uv run fastapi dev "04.1-数据库集成/01-数据库.py"
对照 /docs 观察：建一本书 → 重启服务 → 再查——书还在，这就是「持久化」。
"""

from pathlib import Path
from typing import Annotated

from fastapi import Depends, FastAPI, HTTPException, status
from sqlmodel import Field, Session, SQLModel, create_engine, select

app = FastAPI(title="04.1 数据库集成练习")


# ============ 演示 1：模型即表——一个类身兼两职 ============
class BookBase(SQLModel):
    """公共字段只写一遍：03.3 TODO 2 那套校验规则原样搬过来。"""

    title: str = Field(min_length=1)
    author: str = Field(min_length=1)
    price: float = Field(gt=0)
    rating: float = Field(ge=0, le=5)


class Book(BookBase, table=True):
    """table=True 是关键开关：类从「纯校验模型」升级为「真表」，自动生成 book 表。
    id 是主键、由数据库自增，所以类型是 int | None——客户端创建时不传，入库后数据库填。"""

    id: int | None = Field(default=None, primary_key=True)


class BookCreate(BookBase):
    """请求体模型：故意不含 id——主键轮不到客户端定（03.4 白名单思想）。"""


# ============ 演示 2：engine——全应用只有一个的「连接工厂」 ============
DB_PATH = (
    Path(__file__).parent / "books.db"
)  # 相对本文件定位，从哪个目录启动都指向同一个库
engine = create_engine(
    f"sqlite:///{DB_PATH}",
    # SQLite 默认禁止跨线程复用连接，而 FastAPI 的同步路由跑在线程池里、
    # 每个请求可能换线程——不放开这里，每次请求都会报错。
    # 这是 SQLite 单文件教学场景的妥协；生产上交给连接池与数据库的并发控制。
    connect_args={"check_same_thread": False},
)
# 建表：把所有 table=True 模型翻译成 CREATE TABLE；已存在的表跳过（改表结构它不管，TODO 3）
SQLModel.metadata.create_all(engine)


# ============ 演示 3：session 用 yield 依赖管理——03.5 的真实上岗 ============
def get_session():
    """yield 前是 setup（开会话）、之后是 teardown（关闭）——02.3 生成器的老朋友。
    finally 保证路由哪怕抛了 404 也会关会话；`with Session(engine)` 是同一件事的语法糖。"""
    session = Session(engine)
    try:
        yield session
    finally:
        session.close()


SessionDep = Annotated[Session, Depends(get_session)]  # 起个短名字，各端点复用


# ============ 演示 4：增——POST /books，201 = 已创建 ============
@app.post("/books", status_code=status.HTTP_201_CREATED)
def create_book(data: BookCreate, session: SessionDep) -> Book:
    """/docs 建一本书：响应里 id 已被数据库填好；rating 传 6 → 422（03.3 的校验还在站岗）。"""
    book = Book.model_validate(data)  # 请求模型 → 表模型（03.3 的 model_validate）
    session.add(book)  # 入队：改动先记在 session 里
    session.commit()  # 落库：忘了这步 = 白忙一场，数据没写进文件
    session.refresh(book)  # 把数据库生成的 id 回填到对象上
    return book


# ============ 演示 5：查列表——分页交给数据库 ============
@app.get("/books")
def list_books(session: SessionDep, skip: int = 0, limit: int = 10) -> list[Book]:
    """/books?skip=0&limit=10：offset/limit 翻译成 SQL 的 OFFSET/LIMIT——
    是数据库挑行，不是把全表拉回 Python 再切片（数据量大时差别是性能）。"""
    return session.exec(select(Book).offset(skip).limit(limit)).all()


# ============ 演示 6：查单个 + 404——03.6 的 HTTPException 上岗 ============
@app.get("/books/{book_id}")
def get_book(book_id: int, session: SessionDep) -> Book:
    """先建书再查它的 id → 200；查 999 这种不存在的 id → 404（「没有」不等于「出错」）。"""
    book = session.get(Book, book_id)  # 按主键查，最快的一条路
    if book is None:
        raise HTTPException(status_code=404, detail="书不存在")
    return book


# ============ 演示 7：删——204 = 办好了且无可返回（03.6 的语义沿用） ============
@app.delete("/books/{book_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_book(book_id: int, session: SessionDep) -> None:
    """删除成功 → 204 且响应体为空（所以函数返回 None）；再查同一本 → 404。"""
    book = session.get(Book, book_id)
    if book is None:
        raise HTTPException(status_code=404, detail="书不存在")
    session.delete(book)
    session.commit()


# ============ TODO 1：按作者过滤 ============
# 给 GET /books 加可选查询参数 author: str | None = None：
#   传了就给 select(Book) 追加 .where(Book.author == author)，不传保持原样；
#   注意 .offset / .limit 要排在 .where 后面。在 /docs 里观察 author 是不是可选项。

# ============ TODO 2：PATCH /books/{book_id} 只改价格 ============
# 先写小请求模型 PriceUpdate(price: float = Field(gt=0))——只有价格，没有 id/书名
#   （白名单思想：客户端能改什么，由字段清单说了算，03.4）。
#   PATCH 端点：查到 → 只更新 price 后 commit，返回 200 + 更新后的书；查不到 → 404。

# ============ TODO 3：思考题——create_all 的盲区 ============
# create_all 只补建「不存在的表」：给 BookBase 加个字段 published_year 再重启，
#   已有表的结构不会变，新字段根本写不进去。生产库里的真实数据怎么改表不丢数据？
#   这由「迁移工具」回答——README 的 Alembic 速查表先混个脸熟，项目实战章正式上。
