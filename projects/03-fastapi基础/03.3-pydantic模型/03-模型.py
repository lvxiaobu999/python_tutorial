"""03.3 Pydantic 模型：写模型就是写校验

BaseModel 的字段注解 = 数据契约：缺字段、类型错、超出范围，全部自动 422。
校验规则写在 Field 里，错误详情会告诉你哪个字段、错在哪。

运行（在 projects/03-fastapi基础 目录下）：
    uv run fastapi dev "03.3-pydantic模型/03-模型.py"
重点练习：故意发非法数据，学会读 422 响应里的 loc / msg。
"""

from fastapi import FastAPI
from pydantic import BaseModel, Field

app = FastAPI(title="03.3 Pydantic 模型练习")


# ============ 演示 1：BaseModel 最小示例：字段 + 注解 = 数据契约 ============
class BookIn(BaseModel):
    """最简单的请求体模型：注解本身就是校验规则。"""

    title: str
    price: float
    in_stock: bool = True  # 有默认值 → 可选字段


@app.post("/books")
def create_book(book: BookIn) -> dict:
    """Try it out 发 {"title": "三体", "price": 45}；
    再把 price 删掉（缺必填）或把 title 传成 123（类型不符）看 422。"""
    return {"收到": book.model_dump()}


# ============ 演示 2：Field 校验规则：数字范围与字符串长度 ============
class ReviewIn(BaseModel):
    """Field 给字段加规则：范围、长度、说明文字。"""

    content: str = Field(min_length=5, max_length=200)
    rating: int = Field(ge=1, le=5, description="评分 1~5 星")


@app.post("/reviews")
def create_review(review: ReviewIn) -> dict:
    """rating 传 6 → 422；content 传 "太短" → 422。
    读错误响应里的 loc（哪个字段）和 msg（什么规则）。"""
    return {"收到": review.model_dump()}


# ============ 演示 3：嵌套模型：模型套模型 ============
class AuthorIn(BaseModel):
    name: str
    country: str = "未知"


class DetailedBookIn(BaseModel):
    """字段类型是另一个 BaseModel → JSON 按结构逐层校验。"""

    title: str
    author: AuthorIn  # 嵌套
    tags: list[str] = Field(default_factory=list)  # 可变默认值的标准写法


@app.post("/detailed-books")
def create_detailed_book(book: DetailedBookIn) -> dict:
    """author 传成字符串（不是对象）→ 422，loc 会指到 author 里层。
    正确请求体：{"title": "三体", "author": {"name": "刘慈欣"}, "tags": ["科幻"]}"""
    return {"作者国籍": book.author.country, "标签数": len(book.tags)}


# ============ TODO 1：读 422（本章最重要的肌肉记忆） ============
# 用 /docs 给演示 2 发一个 rating=6，把 422 响应里的 loc 和 msg 抄到下面这个注释里：


# ============ TODO 2：图书模型——期末大作业的核心资产 ============
# 定义 BookCreate：title（str，min_length=1）、author（str，min_length=1）、
#   price（float，必须 > 0）、rating（float，0 ≤ x ≤ 5），
#   加 POST /books-v2 接收它，返回 book.model_dump()。
#   03.4~03.6 和期末大作业都会复用这个模型。


# ============ TODO 3：可选字段的三种请求 ============
# 给 BookCreate 加可选字段 borrowed_by: str | None = None，
#   分别试「不传 / 传 null / 传 "李四"」三种请求体，观察三种结果的差异。
