"""03.2 路由：路径参数、查询参数、请求体与 APIRouter

路由 = 「什么请求」交给「哪个函数」。URL 里能装的信息这一章全讲完：
路径参数（定位资源）、查询参数（过滤/开关）、请求体（提交数据）、APIRouter（拆模块）。

运行（在 projects/03-fastapi基础 目录下）：
    uv run fastapi dev "03.2-路由/02-路由.py"
打开 http://127.0.0.1:8000/docs 对照观察：每个接口的参数是怎么被自动识别的。
"""

from fastapi import APIRouter, FastAPI
from pydantic import BaseModel

app = FastAPI(title="03.2 路由练习")


# ============ 演示 1：路径参数——URL 里定位资源 ============
# {item_id} 占位，函数里同名参数接住；注解 int 让 FastAPI 自动转换 + 校验
@app.get("/items/{item_id}")
def get_item(item_id: int) -> dict:
    """访问 /items/3 试试，再访问 /items/abc 看看 422 校验错误长什么样。"""
    return {"item_id": item_id}


# ============ 演示 2：路径顺序坑——固定路径必须写在通配路径前面 ============
@app.get("/users/me")
def read_current_user() -> dict:
    """演示 3 的通配路径注册在后面，所以 /users/me 能先匹配上；
    把两个路由换个顺序试试，me 就会被当成 user_id。"""
    return {"user": "当前登录用户"}


@app.get("/users/{user_id}")
def read_user(user_id: str) -> dict:
    """注解 str：原样接收，不做转换。"""
    return {"user_id": user_id}


# ============ 演示 3：查询参数——?key=value 传过滤条件 ============
# 不在路径里的函数参数自动变成查询参数：/books?author=鲁迅&in_stock=false
@app.get("/books")
def list_books(author: str | None = None, in_stock: bool = True) -> dict:
    """author 可选（不传是 None）；in_stock 有默认值，?in_stock=false 可覆盖。
    bool 类型会自动把 "true"/"1"/"yes" 转成 True，"false"/"0"/"no" 转成 False。"""
    return {"author": author, "in_stock": in_stock}


# ============ 演示 4：请求体——客户端提交的数据（03.3 细讲模型） ============
class BookIn(BaseModel):
    """最小请求体模型：字段 + 类型注解，FastAPI 自动校验请求体 JSON。"""

    title: str
    price: float


@app.post("/books")
def create_book(book: BookIn) -> dict:
    """浏览器地址栏只能发 GET；用 /docs 的 Try it out 发 POST 试试。
    故意把 price 写成 "贵"——会收到 422，注解在替你把关。"""
    return {"created": book.title, "price": book.price}


# ============ 演示 5：三件套组合——各归各位 ============
@app.put("/users/{user_id}/items/{item_id}")
def update_item(user_id: int, item_id: int, q: str | None = None) -> dict:
    """路径参数（user_id、item_id）+ 查询参数（q）同时用：
    在路径占位符里的走路径，不在的走查询。"""
    result: dict = {"user_id": user_id, "item_id": item_id}
    if q:
        result["q"] = q
    return result


# ============ 演示 6：APIRouter——路由多了以后分模块管理 ============
# 大项目里每个业务一个 router，各自 prefix + tags，最后 include 进 app
router = APIRouter(prefix="/shop", tags=["商店"])


@router.get("/goods")
def list_goods() -> dict:
    """实际路径是 /shop/goods——prefix 统一加前缀，tags 在 /docs 里分组显示。"""
    return {"goods": ["键盘", "鼠标"]}


app.include_router(router)


# ============ TODO 1：路径参数 ============
# 写 GET /books/{book_id}，book_id 注解为 int，返回 {"book_id": book_id}。
#   在 /docs 里分别试 1 和 abc，观察后者的 422 错误详情——找到哪一句在说「类型不对」。


# ============ TODO 2：查询参数过滤 ============
# 写 GET /tasks，带两个查询参数：done（bool，默认 True）、keyword（str 可选）。
#   收到后原样返回。分别试：/tasks、/tasks?done=false、/tasks?done=false&keyword=学习。
@app.get("/tasks")
def list_tasks(done: bool = True, keyword: str | None = None) -> dict:
    """返回任务列表，支持 done 和 keyword 查询参数过滤。"""
    return {"done": done, "keyword": keyword}


# ============ TODO 3：请求体雏形 ============
# 写 POST /tasks，接收请求体模型 TaskIn（title: str，minutes: int = 30），返回收到的内容。
#   这是期末大作业「图书管理 API」的雏形：03.3 会把校验规则加到模型上。


class TaskIn(BaseModel):
    """任务请求体模型：标题 + 预计分钟数（默认 30 分钟）。"""

    title: str
    minutes: int = 30


@app.post("/tasks")
def create_task(task: TaskIn) -> dict:
    """创建任务，返回收到的内容。"""
    return {"title": task.title, "minutes": task.minutes}
