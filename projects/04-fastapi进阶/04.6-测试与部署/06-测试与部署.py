"""04.6 测试与部署：被测小应用——一组故意保持简单的图书 CRUD

本章换个跑法：不再起服务手点 /docs，而是让 pytest 自动验证——
这个文件是「被测对象」，完整测试套件在同目录的 test_06.py 里。

TestClient 原理：FastAPI 的 app 本身就是一个 ASGI 应用。TestClient 不启动
真正的服务器，而是在进程内直接调用它：请求不经过网络、不占端口，所以测试
毫秒级完成，还能精确拿到响应状态码和 JSON——断言不必靠肉眼在 /docs 里猜。

想手动玩依然可以（在 projects/04-fastapi进阶 目录下）：
    uv run fastapi dev "04.6-测试与部署/06-测试与部署.py"
但本章主线的运行方式是跑测试（不是 fastapi dev）：
    uv run pytest "04.6-测试与部署/test_06.py" -v
"""

from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, Field

app = FastAPI(title="04.6 测试与部署练习")


# ============ 1、数据：内存 dict——「被测状态」，也是状态污染的源头 ============
# 真项目的数据在数据库里（04.1），这里故意用模块级 dict：简单到一眼能看懂，
# 也正好暴露测试的经典难题——它活得比任何一次请求、任何一个测试都长。
books: dict[int, dict] = {}


class BookIn(BaseModel):
    """POST /books 的请求体模型——字段规则就是测试要验证的 422 来源（03.3）。"""

    title: str = Field(min_length=1)
    author: str = Field(min_length=1)
    price: float = Field(gt=0)  # 价格必须 > 0：测试会拿一组非法值来撞它
    rating: float = Field(ge=0, le=5)  # 评分限定在 0~5


def reset_books() -> None:
    """清空内存数据。test_06.py 的 fixture 在每个测试前调用它做状态隔离。"""
    books.clear()


# ============ 2、路由：GET /books——图书列表 ============
@app.get("/books")
def list_books(sort: str | None = None) -> dict:
    """最普通的查询，默认返回 200（03.2 路由）。
    sort=price 时按价格升序——为让 test_list_books_sorted_by_price 由红转绿而加（TDD）：
    测试先定义了行为，实现是照着测试补的。"""
    result = list(books.values())
    if sort == "price":
        result.sort(
            key=lambda b: b["price"]
        )  # 就地排的是「副本」，模块级 books 不受影响
    return {"books": result}


# ============ 3、路由：POST /books——创建图书（201 Created，03.4 的状态码） ============
@app.post("/books", status_code=201)
def create_book(book: BookIn) -> dict:
    """校验通过 → 201 + 新书；校验失败 → Pydantic 直接回 422，路由函数根本不执行。"""
    book_id = max(books, default=0) + 1  # 简化版自增 id；真项目交给数据库（04.1）
    data = {"id": book_id, **book.model_dump()}
    books[book_id] = data
    return data


# ============ 4、路由：GET /books/{book_id}——详情，查不到 404（03.6） ============
@app.get("/books/{book_id}")
def get_book(book_id: int) -> dict:
    """存在 → 200 + 单本；不存在 → HTTPException(404)，detail 会进响应体。"""
    if book_id not in books:
        raise HTTPException(status_code=404, detail="图书不存在")
    return books[book_id]


# ============ 5、路由：DELETE /books/{book_id}——删除成功 204 No Content ============
@app.delete("/books/{book_id}", status_code=204)
def delete_book(book_id: int) -> None:
    """204 的语义是「成功且响应体为空」，所以返回 None（03.4 讲过这对搭档）。"""
    if book_id not in books:
        raise HTTPException(status_code=404, detail="图书不存在")
    del books[book_id]
