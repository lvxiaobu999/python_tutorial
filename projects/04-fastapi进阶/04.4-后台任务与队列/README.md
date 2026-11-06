# 04.4 后台任务与队列

> 发邮件、写审计日志这类活儿，用户不该等它做完。`BackgroundTasks` 把函数登记成任务，等响应发出去之后再执行；
> 但它只活在当前进程里——要可靠、可重试、可扩容，就需要消息队列（Celery/RQ）。本章先学内置方案，再立概念。

## 知识点速查

### 1. BackgroundTasks 三步：声明函数 → add_task 登记 → 自动执行

```python
def send_notification(to: str, title: str) -> None:   # ① 普通函数，随便怎么写
    time.sleep(3)  # 慢活儿
    print(f"已发给 {to}：《{title}》")

@app.post("/books")
def create_book(title: str, tasks: BackgroundTasks) -> dict:  # ② 参数里声明，框架注入
    tasks.add_task(send_notification, to, title)      # ③ 只登记，不调用
    return {"message": "创建成功"}
```

响应发送完之后，FastAPI 按登记顺序逐个调用任务函数——用户完全不用等。

### 2. add_task 的参数怎么传
`add_task(函数本身, 参数1, 参数2, ...)`：第一个参数是**函数名**（不是 `函数(...)`——加了括号就是当场调用，任务等于没排上）；
后面的参数要等任务真正执行时才传给它。关键字参数接在后面：`add_task(fn, to, title, priority=1)`。

### 3. 执行时机：响应发送之后
请求时间线：依赖（03.5）→ 路由函数 → 响应发给用户 → **这里才开始跑后台任务**。所以任务慢、任务抛异常，都不影响用户已经拿到的响应——用户看到的一直是「秒回」。

### 4. 与 yield 依赖 teardown 的分工（03.5 呼应）

| | yield 依赖 teardown | BackgroundTasks |
|---|---|---|
| 干什么 | 清理**本请求**的资源（关连接、还锁） | 干**与响应无关**的慢活儿（发邮件、写日志） |
| 怎么声明 | 依赖函数里 `yield` 之后的代码 | 路由参数注入 `tasks`，用 `add_task(...)` 登记 |
| 跑在何时 | 本请求收尾时，和这个请求绑死 | 响应发送之后，按登记顺序逐个跑 |
| 一句话 | 「借了要还」 | 「回完话再干活」 |

### 5. BackgroundTasks 的边界（什么时候不够用）
- **进程内**：任务和 API 跑在同一个 Python 进程里，抢同一份 CPU/内存，任务重了接口也变慢。
- **随进程死**：服务重启或崩溃，排队中、执行中的任务直接消失，不留任何记录。
- **不能重试**：函数抛异常不会重试、不会告警，只能翻终端日志。

## 易错点
- 任务函数里抛异常：**响应早就发出去了**，用户看到的是成功，异常只打到服务终端——后台任务必须看日志，否则就是静默失败。
- 把大活儿全塞 BackgroundTasks：它和接口共用同一个进程，「延后」不等于「扩容」，任务一多正常请求跟着遭殃。
- `time.sleep` 放进 `async def` 路由会卡死整个事件循环，所有接口一起瘫（02.5 的坑）；放进 `def` 路由只占线程池一条线程，本章演示 1 就是这么写的。
- `tasks.add_task(send_notification(to, title))` 加了括号 = 现在就调用并登记了返回值 `None`，什么都不会执行。

## 概念指南：Celery/RQ——把队列搬到进程外（知道即可）
BackgroundTasks 的三个短板（进程内、随进程死、不能重试），生产方案是消息队列，三个角色：
- **producer（生产者）**：你的 FastAPI。只干一件事：往队列扔一条消息（"给 xx 发邮件"），扔完立刻回响应。
- **broker（中间人）**：消息队列本身（Redis / RabbitMQ）。消息先存在这里，谁有空谁领走——任务不随 API 进程一起死，这就是可靠性的来源。
- **worker（工人）**：独立于 API 的进程，从 broker 领消息执行；挂了重启、失败重试、不够就多开几个 worker（横向扩容）。
为什么需要消息队列：**解耦**（API 不干重活，只发消息）、**重试**（任务有记录，失败能重跑）、**横向扩容**（worker 随便加，不动 API）。
Windows 现实注意：Celery 5 在 Windows 上必须加 `--pool=solo` 才能跑（默认 prefork 池不兼容），broker 还得装 Redis
（官方不支持 Windows，一般走 Docker/WSL）。建议等有 Docker 环境再上手，本章先建立 producer/broker/worker 的概念就够了。

## 进阶提示
- 任务函数也能是 `async def`，里面要用 `asyncio.sleep(...)` 而不是 `time.sleep(...)`（别阻塞事件循环）。
- 用 TestClient 测不出「响应先回、任务后跑」：它会等后台任务执行完才返回。要测「立即返回」，把慢函数
  替换成快的假函数再断言耗时（04.6 测试章见）。

## 学习顺序与练习

启动 `uv run fastapi dev "04.4-后台任务与队列/04-后台任务.py"`，先在 /docs 体验演示 1 的 3 秒卡顿，
再对比演示 2 的秒回、盯着终端看 print 迟到，然后完成 TODO：

1. TODO 1：把演示 1 的发通知挪进后台任务，用 `curl -w "%{time_total}"` 对比两个接口耗时。
2. TODO 2：DELETE /books/{book_id}——404 之外，删成功后异步发「删除通知」。
3. TODO 3：思考题——服务重启时排队中的任务会怎样？想清楚再回看 Celery 指南。
