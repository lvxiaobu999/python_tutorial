"""03.4 响应模型：出口也要管

请求模型管「进来的数据」（03.3），response_model 管「出去的数据」：
过滤敏感字段、声明状态码语义、读写 Header 与 Cookie。

运行（在 projects/03-fastapi基础 目录下）：
    uv run fastapi dev "03.4-响应模型/04-响应模型.py"
"""

from typing import Annotated

from fastapi import Cookie, FastAPI, Header, Response, status
from pydantic import BaseModel

app = FastAPI(title="03.4 响应模型练习")


# ============ 演示 1：response_model——响应的「白名单」 ============
class UserOut(BaseModel):
    """响应模型：只声明允许出现在响应里的字段——没有 password。"""

    username: str
    email: str


@app.get("/users/{username}", response_model=UserOut)
def get_user(username: str) -> dict:
    """内部数据带密码，但 response_model 只放行声明的字段——响应里看不到密码。
    打开 /docs 看这个接口的 Responses 结构：也没有 password。"""
    return {
        "username": username,
        "email": f"{username}@example.com",
        "password": "绝密123456",  # 会被 response_model 过滤掉
    }


# ============ 演示 2：状态码——「成功」也分很多种 ============
class OrderIn(BaseModel):
    item: str


@app.post("/orders", status_code=status.HTTP_201_CREATED)
def create_order(order: OrderIn) -> dict:
    """创建成功用 201 而不是 200——语义精确；/docs 里会显示这个预期状态码。"""
    return {"order_id": 1, "item": order.item}


# ============ 演示 3：读请求头与 Cookie ============
# Annotated[类型, 附加信息]：给类型挂元数据的写法，FastAPI 靠第二项识别参数来源
@app.get("/whoami")
def whoami(
    user_agent: Annotated[str | None, Header()] = None,
    session_id: Annotated[str | None, Cookie()] = None,
) -> dict:
    """Header() 把 user_agent 映射到 HTTP 头 User-Agent（下划线即连字符）。
    先访问 /login 种下 Cookie，再回来访问 /whoami 看 session_id 出现。"""
    return {"user_agent": user_agent, "session_id": session_id}


# ============ 演示 4：写 Cookie——给函数加 Response 参数 ============
@app.get("/login")
def login(response: Response) -> dict:
    """声明 response: Response 就能设置 Cookie / 响应头；返回值照常返回，互不影响。"""
    response.set_cookie(key="session_id", value="abc123", max_age=3600)
    return {"message": "已种下 session_id Cookie"}


# ============ TODO 1：响应模型过滤 ============
# 定义 BookOut（只有 title / author / rating 三个字段），写 GET /books-secret，
#   函数里返回带内部字段的数据（比如 cost 进价），用 response_model 把 cost 滤掉。


# ============ TODO 2：状态码 ============
# 写 POST /books-secret，接收 BookOut 同结构的请求体，创建成功返回 201；
#   到 /docs 看这个接口文档里预期的响应码显示成了什么。


# ============ TODO 3：Cookie 闭环 ============
# 依次访问 /login → /whoami，确认 session_id 出现；
#   再打开浏览器 DevTools → Application → Cookies，亲眼看到这个 Cookie。
