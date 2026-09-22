# 02.5 异步编程

> 这一章解决「一个线程怎么同时等很多个 IO」。网络请求、数据库查询、读文件时 CPU 都在干等——异步把等待时间让给别人用。**FastAPI 的高并发就建立在这上面**：`async def` 路由在 `await` 时让出线程去服务别的请求。这是本模块的重头戏，多花时间。

## 知识点速查

### 1. 并发 vs 并行，什么任务适合异步

| 概念 | 含义 | 需要几个核 |
|------|------|-----------|
| 并行（parallel） | 多个任务**同时**执行 | 多核（真同时） |
| 并发（concurrent） | 多个任务**交替推进**，宏观上「一起」 | 单核也行 |

| 任务类型 | 例子 | 该用什么 |
|----------|------|----------|
| IO 密集 | 网络请求、查数据库、读写文件 | **asyncio**（等待时可切换去干别的） |
| CPU 密集 | 图像处理、大量计算 | 多进程 multiprocessing（异步帮不上忙） |

记忆：**等待多 → 异步；计算多 → 多进程**。asyncio 是单线程并发，不是并行。

### 2. 协程：async def 与 await

```python
import asyncio


async def fetch(name: str) -> str:          # async def 定义「协程函数」
    print(f"{name} 开始")
    await asyncio.sleep(1)                  # await：等待时把控制权还给事件循环
    print(f"{name} 结束")
    return f"{name} 的结果"


coro = fetch("任务A")       # 调用协程函数：不执行！只返回一个「协程对象」
result = await coro         # await 才真正执行它并等结果（只能在 async 函数里写）
```

- 调用 `async def` 函数 ≠ 执行它，就像调用生成器函数不执行一样（呼应 02.3）。
- `await x`：等 x 完成、拿结果；**等待期间当前协程挂起，线程去跑别的协程**——这就是「让出」。
- `await` 只能出现在 `async def` 内部；协程对象必须被 await（或交给事件循环），否则报 "coroutine was never awaited"。

### 3. 事件循环与 asyncio.run

```python
async def main() -> None:
    ...                                  # 异步世界的入口


asyncio.run(main())        # 启动事件循环：单线程调度器，驱动所有协程
```

事件循环的理解：一个不断转的调度员，维护一张「就绪协程」清单；谁在 await IO 就先把谁挂起，IO 好了再把它放回来。整个程序里通常只 `asyncio.run` 一次，在最高层。

### 4. 串行 await vs 并发 gather（本章核心）

```python
import asyncio
import time


async def job(n: float) -> str:
    await asyncio.sleep(n)                # 模拟耗时 n 秒的网络请求
    return f"done {n}"


async def serial() -> None:               # 串行：一个等完才下一个
    await job(1)
    await job(1)
    await job(1)                          # 总耗时 ≈ 3 秒


async def concurrent() -> None:           # 并发：三个任务一起等
    results = await asyncio.gather(       # gather：同时启动多个协程，全部完成再返回
        job(1), job(1), job(1)
    )
    print(results)                        # 总耗时 ≈ 1 秒！
```

逐个 `await` = 排队；`asyncio.gather(*协程们)` = 一起上。**这是新手最常犯的错：函数都是 async 的，但逐个 await，结果一点没快**。

### 5. 任务的其他姿势

```python
# create_task：立刻把协程排入事件循环（不等 await）
task = asyncio.create_task(job(1))
result = await task

# TaskGroup（3.11+，推荐）：一个失败自动取消其余，异常带上下文
async with asyncio.TaskGroup() as tg:
    t1 = tg.create_task(job(1))
    t2 = tg.create_task(job(1))
print(t1.result(), t2.result())

# 超时控制（3.11+）
async with asyncio.timeout(2):            # 2 秒内没完成 → 抛 TimeoutError
    await job(5)
```

### 6. 一张图记住执行流

```
串行：  job1 ██░░░░░░ → job2 ██░░░░░░ → job3 ██░░░░░░      合计 3 秒
并发：  job1 ██░░░░░░
        job2 ██░░░░░░     三者共享同一段「等待」           合计 1 秒
        job3 ██░░░░░░
（█ 执行片段；░ 等待时事件循环在服务别的任务）
```

## 易错点

- `fetch("A")` 只创建了协程没执行，忘 await 会看到 RuntimeWarning: coroutine was never awaited。
- 在 async 函数里用 `time.sleep(1)`——它不放手，**整个事件循环被卡住**，所有协程都动不了；必须 `await asyncio.sleep(1)`。
- 逐个 `await` 以为是并发，实际是串行（本章节最核心的坑，练习 2 亲手对比）。
- 在普通 `def` 里写 `await`——语法错误；在 async 函数外跑协程要用 `asyncio.run`。
- `gather` 里某个协程抛异常，其他任务**不会自动取消**（还会继续跑完），要异常安全用 TaskGroup。
- CPU 密集任务放 async 里毫无收益：单线程里算 1 秒，谁也抢不到 CPU。

## 进阶提示

- 真实网络请求用 `httpx`：`uv add httpx` 后 `async with httpx.AsyncClient() as client:` + gather，就是并发爬虫/批量调 API 的标准写法（期末大作业选做它的模拟版）。
- **FastAPI 关联**：`@app.get("/")` 的处理函数写成 `async def` 时，函数内 await 数据库/LLM 期间，uvicorn 的线程继续处理其他请求——这就是「async 路由高并发」的全部秘密；写成普通 `def` 时 FastAPI 会自动丢进线程池，同样不阻塞。
- 异步生成器 `async def + yield`：每生成一段就交出去，LLM 流式输出（打字机效果）就靠它，模块 05/06 见。
- 并发数量要控制：几百个请求同时发要配信号量 `asyncio.Semaphore(10)` 限流。

## 学习顺序与练习

先把演示文件跑起来，对照输出读懂「1 秒 vs 3 秒」；然后完成 TODO。练习 2 做完后把任务数改成 10 再跑一遍，并试着回答：为什么耗时几乎不变？

基础 TODO（见 `01-异步并发.py`）：
1. `fake_fetch(url)`：`await asyncio.sleep(0.5)` 模拟请求，返回 `"url 的内容"`。
2. 串行抓 3 个 url 并用 `time.perf_counter` 计时（期望 ≈1.5 秒）。
3. 用 `gather` 并发抓同样 3 个（期望 ≈0.5 秒），打印两种耗时对比。
4. 选做：`TaskGroup` 版本 + `asyncio.timeout` 给慢任务加超时。
