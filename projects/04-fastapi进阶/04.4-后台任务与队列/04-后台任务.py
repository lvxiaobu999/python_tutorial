"""04.4 后台任务与队列：响应先回话，慢活儿后台干

发邮件、写审计日志这类「用户不用等结果」的活儿，直接写进路由会让请求卡住。
BackgroundTasks 让你把函数登记成任务，FastAPI 在「响应发送完之后」再执行它。
和 03.5 的 yield 依赖 teardown 同为「请求后逻辑」，但分工不同：
yield 管「本请求资源的清理」，BackgroundTasks 管「响应完用户之后干活」。

运行（在 projects/04-fastapi进阶 目录下）：
    uv run fastapi dev "04.4-后台任务与队列/04-后台任务.py"
对照 /docs 观察：同一个「发通知」，卡 3 秒的和秒回的差在哪。
"""

import time

from fastapi import BackgroundTasks, FastAPI, HTTPException

app = FastAPI(title="04.4 后台任务练习")

BOOKS = {
    1: {"title": "三体", "available": True},
    2: {"title": "活着", "available": True},
}  # 模块级字典模拟数据库（04.1 换成 SQLModel 后，任务函数照旧这么写）


def _now() -> str:
    """统一打时间戳：观察后台任务的执行顺序，全靠终端里这几行的时间先后。"""
    return time.strftime("%H:%M:%S")


# ============ 演示 1：反例——把慢活儿直接写进路由 ============
@app.post("/books-slow")
def create_book_slow(title: str, to: str) -> dict:
    """去 /docs 执行它：点 Execute 后要转 3 秒才看到响应——用户在干等通知发完。
    观察什么：响应耗时约 3 秒；终端里的 print 和响应几乎同时出现。"""
    # 注意这里必须是 def 而不是 async def：FastAPI 会把 def 路由丢进线程池跑，
    # time.sleep(3) 只卡住这一条线程；若写进 async def，会卡死整个事件循环，
    # 所有接口一起瘫痪（02.5 讲过的坑，本章反例正是它最典型的翻车现场）。
    time.sleep(3)  # 模拟「发通知邮件」的真实网络耗时（真实场景是 SMTP/API 调用）
    print(f"[{_now()}] 通知已发给 {to}：《{title}》")
    return {"message": "图书已创建，但你为发通知多等了 3 秒", "title": title}


# ============ 演示 2：BackgroundTasks——先回话，再干活 ============
def send_notification(to: str, book_title: str) -> None:
    """后台任务就是一个普通函数，FastAPI 在响应发完之后才调用它。
    与 03.5 的 yield 依赖 teardown 同为「请求后逻辑」，分工却不同：
    yield 管「本请求资源的清理」，这里管「响应完用户之后干活」。"""
    print(f"[{_now()}] 开始发通知……")
    time.sleep(3)  # 反例里这 3 秒用户在干等；现在只有「后台」在等
    print(f"[{_now()}] 通知已发给 {to}：《{book_title}》")


@app.post("/books-fast")
def create_book_fast(title: str, to: str, tasks: BackgroundTasks) -> dict:
    """观察什么：/docs 里执行，响应立刻回来（耗时远小于 3 秒）；再看运行
    fastapi dev 的终端——两条 print 在响应之后才陆续出现，明显晚半拍。
    （用 TestClient 测不出这个效果：它会等任务跑完才返回，见 README 进阶提示。）"""
    # add_task 传的是「函数本身 + 参数列表」：此刻只登记，不是现在调用——
    # 写成 send_notification(to, title) 就变成当场执行，任务等于没排上。
    tasks.add_task(send_notification, to, title)
    return {"message": "图书已创建，通知正在后台发", "title": title}


# ============ 演示 3：多参数任务 + 一次请求排多个任务 ============
def write_audit_log(action: str, book_id: int, operator: str) -> None:
    """任务函数想带几个参数都行：add_task(函数, 参数1, 参数2, ...) 按位置依次对应。"""
    time.sleep(1)  # 故意比发通知快，方便在终端看清「按登记顺序依次执行」
    print(f"[{_now()}] 审计日志：{operator} 对图书 {book_id} 执行了「{action}」")


@app.post("/books/{book_id}/borrow")
def borrow_book(book_id: int, tasks: BackgroundTasks, to: str = "admin@ex.com") -> dict:
    """观察什么：响应秒回；终端约 1 秒后出现审计日志、约 4 秒后出现通知——
    多个任务按 add_task 的登记顺序依次执行，不是同时并发跑。"""
    book = BOOKS.get(book_id)
    if book is None:
        raise HTTPException(status_code=404, detail="图书不存在")  # 03.6 的老朋友
    if not book["available"]:
        raise HTTPException(status_code=409, detail="图书已被借出")
    book["available"] = False
    tasks.add_task(write_audit_log, "借出", book_id, "admin")  # 任务 1：先记审计日志
    tasks.add_task(send_notification, to, book["title"])  # 任务 2：再发借书通知
    return {"message": "借书成功，日志与通知交给后台", "book": book}


# ============ TODO 1：把反例改成正版 ============
# 新增 POST /books-fixed：同样的「发通知」，但用 tasks.add_task 挪到后台，
#   用 /docs 或 curl -w "%{time_total}" 对比它和 /books-slow 的响应耗时差多少。
@app.post("/books-fixed")
def create_book_fixed(title: str, to: str, tasks: BackgroundTasks) -> dict:
    tasks.add_task(send_notification, to, title)
    return {"message": "图书已创建", "title": title}


# ============ TODO 2：删除图书 + 异步「删除通知」 ============
# 加 DELETE /books/{book_id}：不存在抛 404（03.6 的写法），删除成功后用后台任务
#   发一封「删除通知」（复用 send_notification，想想 to 和书名该传什么）。
@app.delete("/books/{book_id}")
def del_book(book_id: int, tasks: BackgroundTasks) -> dict:
    book = BOOKS.get(book_id)  # get 默认返回 None，第二个参数可省
    if book is None:
        raise HTTPException(status_code=404, detail="图书不存在")
    del BOOKS[book_id]
    # 登记任务时参数当场求值：局部变量 book 还引用着字典对象，
    # 所以「先删再登记」也能取到书名（登记的是值，不是「到时候去 BOOKS 里找」）
    tasks.add_task(send_notification, "游客", book["title"])
    return {"deleted": book_id, "message": "删除成功"}


# ============ TODO 3：思考题（不写代码，先想再翻 README） ============
# 服务重启时，正在排队/执行中的 BackgroundTasks 会怎样？任务有记录、能重试吗？
#   想清楚这一点，再去看 README 的 Celery 概念指南——那就是为补这些短板而生。
#
# 【答案】BackgroundTasks 是「进程内的待办清单」：add_task 只是把函数和参数记在
#   当前进程的内存里，响应发完后由同一个进程顺手执行。
#   → 服务重启：排队中 / 执行中的任务直接丢失，无记录、无重试、无持久化。
#   要「重启不丢、失败重试、多机分担」，得把任务挪出进程——这就是 Celery 的位置：
#   任务写进 Redis / RabbitMQ 这样的中转仓库（broker），由独立的 worker 进程
#   领取执行，失败可重试、有记录可查。
#   ⚠️ 「任务存放在 Redis/RabbitMQ，重启不影响执行」是 Celery 的特性，
#   对本章的 BackgroundTasks 不成立——两者的本质分界就在「任务住在哪个进程」。
