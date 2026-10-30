"""03.6 错误处理：出错了怎么办

API 的错误要「说得清」：状态码 + 错误详情。
HTTPException 覆盖 90% 场景；自定义异常 + 异常处理器应对业务专属错误。

运行（在 projects/03-fastapi基础 目录下）：
    uv run fastapi dev "03.6-错误处理/06-错误处理.py"
对比体验：book_id=1（200）和 book_id=99（404 + JSON 详情）。
"""

from fastapi import FastAPI, HTTPException, Request, status
from fastapi.responses import JSONResponse

app = FastAPI(title="03.6 错误处理练习")

fake_books: dict[int, dict] = {
    1: {"title": "三体", "author": "刘慈欣", "price": 45.0},
    2: {"title": "活着", "author": "余华", "price": 39.9},
}


# ============ 演示 1：HTTPException——带着状态码报错 ============
@app.get("/books/{book_id}")
def get_book(book_id: int) -> dict:
    """book_id=1 → 200；book_id=99 → 404 + {"detail": ...}。
    反例是 return {"error": ...}：状态码还是 200，客户端没法可靠判断成败。"""
    if book_id not in fake_books:
        raise HTTPException(status_code=404, detail=f"book_id={book_id} 不存在")
    return fake_books[book_id]


# ============ 演示 2：自定义异常 + 全局处理器 ============
class BookNotFoundError(Exception):
    """业务专属异常：含义自解释，抛的时候不用记状态码。"""


@app.get("/library/{book_id}")
def library_get(book_id: int) -> dict:
    """业务代码只管抛业务异常，长什么样交给下面的处理器。"""
    if book_id not in fake_books:
        raise BookNotFoundError(book_id)
    return fake_books[book_id]


@app.exception_handler(BookNotFoundError)
async def book_not_found_handler(
    request: Request, exc: BookNotFoundError
) -> JSONResponse:
    """全局兜底：任何地方抛 BookNotFoundError，都统一变成这个 404 响应。"""
    return JSONResponse(
        status_code=status.HTTP_404_NOT_FOUND,
        content={"message": f"第 {exc.args[0]} 号书不存在"},
    )


# ============ 演示 3：把错误写进文档：responses ============
@app.get(
    "/catalog/{book_id}",
    responses={404: {"description": "书不存在"}},  # 只影响 /docs 展示，不影响行为
)
def catalog_get(book_id: int) -> dict:
    """打开 /docs 对比：这个接口多了 404 响应的说明——前端照着写错误处理。"""
    if book_id not in fake_books:
        raise HTTPException(status_code=404, detail="书不存在")
    return fake_books[book_id]


# ============ TODO 1：删除接口 ============
# 写 DELETE /books/{book_id}：书存在 → 删除并返回 204（提示：status_code=status.HTTP_204_NO_CONTENT，函数返回 None）；
#   不存在 → 抛 404。删掉的书再查一次，确认真的没了。


# ============ TODO 2：业务异常 ============
# 自定义 PriceTooHighError，写 POST /books-checked 接收 {"title": str, "price": float}：
#   price > 1000 时抛出，并注册异常处理器。
#   处理器返回哪个状态码由你决定（422 或 400？），在下面写一句你的理由：


# ============ TODO 3：验收彩排 ============
# 这就是期末大作业的验收路径：在 /docs 里把 200、404、422 三种响应各触发一次。
