"""04.3 中间件与 CORS：给整个应用套上「洋葱层」

中间件是包住整个应用的函数：请求进来先穿过它，响应出去再穿回来。
它比 03.5 的 yield 依赖管得宽——404、HTTPException、/docs 页面也照样穿过它。
CORS 解决的是「浏览器里的页面 fetch 别的源被拦」：规矩定在浏览器，不在服务器。

运行（在 projects/04-fastapi进阶 目录下）：
    uv run fastapi dev "04.3-中间件与CORS/03-中间件.py"
终端观察：随便发什么请求（包括打错的路径），都会打印一行 [中间件]。
浏览器观察：双击同目录 cors-test.html，F12 看跨域请求如何被拦（步骤见 README）。
"""

import time
import uuid
from collections.abc import Awaitable, Callable

from fastapi import FastAPI, HTTPException, Request, Response
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI(title="04.3 中间件与 CORS 练习")


# ============ 演示 1：计时中间件——包住整个应用的「洋葱层」 ============
# 对比 03.5：yield 依赖只包住「声明了它的那几个端点」；中间件是洋葱层，
# 包住整个应用——/docs、404、异常响应统统要从它这里穿进穿出。
# 类型标注在「源头」：call_next 进来是啥、response 出去是啥写进签名，
# Pylance 就能推断 response 的类型并检查 headers 键名——不需要对结果做 TS 式的 as/cast
@app.middleware("http")
async def add_process_time(
    request: Request, call_next: Callable[[Request], Awaitable[Response]]
) -> Response:
    """必须是 async def（02.5 事件循环）：它要 await 里层算完才能拿到响应。

    call_next(request) 就是「放行」：把请求交给洋葱的里层（路由 / 404 / 异常处理器），
    它返回时里层已产出响应，我们只做收尾：记耗时、补一个响应头。
    去 /docs 随便调一个接口 → F12 看响应头多了 X-Process-Time-ms；终端多了 [中间件] 一行。
    """
    start = time.perf_counter()
    response = await call_next(request)
    cost_ms = (time.perf_counter() - start) * 1000
    response.headers["X-Process-Time-ms"] = f"{cost_ms:.1f}"
    print(
        f"[中间件] {request.method} {request.url.path} → {response.status_code} {cost_ms:.1f}ms"
    )
    return response


# ---------- 借用的老朋友：03.6 的图书接口，给中间件当「穿过对象」 ----------
BOOKS = {1: "三体", 2: "活着", 3: "红楼梦"}


@app.get("/books")
def list_books() -> dict:
    """正常 200。响应头里的 X-Process-Time-ms 是中间件加的——路由代码从没写过它。"""
    return {"books": list(BOOKS.values())}


@app.get("/books/{book_id}")
def get_book(book_id: int) -> dict:
    """id 不存在抛 404（03.6 的 HTTPException）：异常在洋葱内层被翻译成 404 响应，
    穿出到中间件时已经是普通响应——print 照样显示 404 与耗时，这就是「管得宽」。"""
    if book_id not in BOOKS:
        raise HTTPException(status_code=404, detail="书不存在")
    return {"id": book_id, "title": BOOKS[book_id]}


# ============ 演示 2：CORSMiddleware——给「浏览器的跨域请求」放行 ============
# 同源 = 协议 + 域名 + 端口全都相同，缺一个就是跨域。
# 浏览器里的页面（模块 05 的前端）fetch 别的源时，服务器响应必须带上
# Access-Control-Allow-Origin 表明「我允许这个源」，浏览器才肯把响应交给页面的 JS。
# 注意：这只是浏览器的规矩——curl / Postman / TestClient 没有它，怎么发都是通的。
# 观察：curl -i -H "Origin: http://localhost:3000" http://127.0.0.1:8000/books
#   → 响应里有 access-control-allow-origin；换个不在名单的 Origin → 这个头消失。
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],  # 白名单：模块 05 前端开发服务器的地址
    allow_methods=["GET", "POST"],  # 允许跨域使用的 HTTP 方法
    allow_headers=["X-Custom-Token"],  # 允许携带的自定义头（不在名单里，预检直接失败）
)
# 洋葱顺序：add_middleware 后注册的包在最外层 → CORS 套在计时中间件外面。
# 所以预检 OPTIONS 被拒（400）时终端没有 [中间件] print——请求根本没穿进内层。


# ============ TODO 1：日志中间件 ============
# 再注册一个中间件：每个请求 print 方法、路径、状态码、耗时，并补上
#   User-Agent（request.headers.get("user-agent")），拼成一行访问日志。
# 想清楚：要让这一层包在演示 1 计时中间件的「外面」，注册语句该写在文件的哪一行之前？
@app.middleware("http")
async def add_process_info(
    request: Request, call_next: Callable[[Request], Awaitable[Response]]
) -> Response:
    """访问日志：方法、路径、状态码、耗时、User-Agent，一行拼齐。
    注册在演示 1 之后（第 29 行 < 第 92 行）→ 后注册的包最外层，本层在计时层外面。
    前缀写 [访问日志] 而不是沿用 [中间件]：两层都打印时终端分得清是哪层在说话。"""
    start = time.perf_counter()
    response = await call_next(request)
    cost_ms = (time.perf_counter() - start) * 1000
    user_agent = request.headers.get("user-agent")
    print(
        f"[访问日志] {request.method} {request.url.path} → {response.status_code} "
        f"{cost_ms:.1f}ms UA={user_agent}"
    )
    return response


# ============ TODO 2：X-Request-ID 响应头 ============
# 给每个响应加 X-Request-ID 头，值用 uuid.uuid4() 生成——排查日志时靠它串联同一个请求。
# 思考：加头必须在 call_next 之后（拿到 response 才能改），
#   那如果想在「进路由之前」就拿到这个 id 并打印进日志，代码该放在哪一段？
@app.middleware("http")
async def add_process_request_id(
    request: Request, call_next: Callable[[Request], Awaitable[Response]]
) -> Response:
    """X-Request-ID：入向（call_next 之前）生成并打印——这就是思考题的答案：
    call_next 之前的代码在「进路由之前」执行；出向写进响应头供日志串联。
    往里带数据用 request.state（request.headers 只读，赋值直接 TypeError）；
    往外带数据用 response.headers。"""
    request_id = str(uuid.uuid4())  # cast 只贴标签不转换，真转换要用 str()
    request.state.request_id = (
        request_id  # 路由/依赖里可用 request.state.request_id 取回
    )
    print(f"[Request-ID] {request_id} → {request.method} {request.url.path}")
    response = await call_next(request)
    response.headers["X-Request-ID"] = request_id
    return response


@app.get("/state")
def get_state(request: Request):
    return {"uuid": request.state.request_id}


# ============ TODO 3：思考题（不用写代码） ============
# allow_origins=["*"] 与 allow_credentials=True 为什么不能同时用？
# 提示：浏览器规范禁止这个组合（ACAO:* 的响应不许再声明可携带 Cookie）。
#   "*" 意味着任何网站都能读你的响应；若还允许带 Cookie，任意网站都能
#   拿着用户的登录态来调你的接口，等于跨站攻击门户大开。
#   starlette 遇到这个组合不会报错，而是把 "*" 悄悄换成「回显请求的 Origin」，
#   效果等同于对全部源放行——防护等于没有，所以自己别这么配。
