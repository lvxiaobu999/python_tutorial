"""异步编程：async/await、事件循环、串行 vs gather 并发

async def 定义协程函数，调用它只创建协程、不执行；await 才执行并在等待 IO 时
把控制权还给事件循环。逐个 await 是串行，asyncio.gather 才是真并发。
"""

import asyncio
import random
import time


# ============ 演示 1：协程与 await ============
async def say_after(delay: float, message: str) -> str:
    await asyncio.sleep(delay)  # await：挂起自己，把线程让给事件循环
    return message


# coroutine = say_after(1, "hi")     # ← 只调用不 await：什么都不发生（常见坑）
result = asyncio.run(say_after(0.1, "hi"))  # asyncio.run：驱动一个协程跑完
print(result)  # hi


# ============ 演示 2：串行 vs 并发（本章核心） ============
class RequestError(Exception):
    """自定义异常：模拟「请求失败」。起个名字比笼统的 RuntimeError 好定位。"""


async def job(name: str, seconds: float, flaky: bool = False) -> str:
    print(f"{name} 开始 @{time.perf_counter() - T0:.2f}s")
    await asyncio.sleep(seconds)  # 模拟网络 IO：此刻线程可以去跑别的协程
    if flaky:  # 默认关闭，演示 1/2/3 保持可复现；想模拟失败时传 flaky=True
        n = random.randint(0, 99)  # 随机 int
        if n % 7 == 0:  # 能被 7 整除（含 0，约 1/7 概率）→ 请求失败
            raise RequestError(f"{name} 请求失败（随机数 {n} 被 7 整除）")
    print(f"{name} 结束 @{time.perf_counter() - T0:.2f}s")
    return f"{name}完成"


T0 = time.perf_counter()


async def serial() -> list[str]:
    """逐个 await：一个等完才轮到下一个，总耗时 = 各任务之和。"""
    r1 = await job("A", 1)  # 等 1 秒
    r2 = await job("B", 1)  # 再等 1 秒
    r3 = await job("C", 1)  # 再等 1 秒
    return [r1, r2, r3]


async def concurrent() -> tuple[str, str, str]:
    """gather：三个任务同时进入等待，总耗时 ≈ 最长的那个。"""
    results = await asyncio.gather(
        job("A", 1),
        job("B", 1),
        job("C", 1),
    )
    return results


async def main() -> None:
    t = time.perf_counter()
    await serial()
    print(f"串行总耗时：{time.perf_counter() - t:.2f} 秒（≈3秒）\n")

    t = time.perf_counter()
    results = await concurrent()
    print(f"并发总耗时：{time.perf_counter() - t:.2f} 秒（≈1秒）")
    print(results)


asyncio.run(main())


# ============ 演示 3：TaskGroup 与超时（3.11+） ============
async def guarded() -> None:
    async with asyncio.timeout(1.5):  # 整块限时 1.5 秒
        async with asyncio.TaskGroup() as tg:  # 一个失败会自动取消其余
            tg.create_task(job("X", 1))
            tg.create_task(job("Y", 1))
    print("TaskGroup 全部完成")


asyncio.run(guarded())


# ============ 演示 4：捕获单个失败（练习 4 热身） ============
# 协程里的异常和普通函数一样向上传播，到 await 它的那一行，try/except 照常能抓。
async def flaky_demo() -> None:
    for i in range(3):  # 多跑几次，约 1/7 概率失败，感受随机性
        try:
            print(await job(f"F{i}", 0.2, flaky=True))
        except RequestError as e:
            print(f"抓到失败：{e}")


asyncio.run(flaky_demo())

print("============ 练习答案验证 ============")


# ============ 练习 1：模拟抓取函数 ============
# TODO 1：写协程函数 fake_fetch(url: str) -> str：
#   a. 打印「开始抓取 url」。
#   b. await asyncio.sleep(0.5) 模拟网络延迟。
#   c. 返回 f"{url} 的页面内容(200 OK)"。
async def fake_fetch(url: str) -> str:
    print(f"开始抓取 {url}")  # TODO 1a：串行/并发的时序差异，全靠这行观察
    await asyncio.sleep(0.5)
    return f"{url} 的页面内容(200 OK)"


result = asyncio.run(fake_fetch("https://github.com"))

print(result)


# ============ 练习 2：串行计时 ============
# TODO 2：写 async 函数 fetch_serial(urls)：
#   a. urls = ["https://a.com", "https://b.com", "https://c.com"]。
#   b. for 循环里逐个 await fake_fetch(url)，收集结果。
#   c. 在外层用 time.perf_counter() 计时并打印「串行耗时 x.xxx 秒」（期望 ≈1.5）。
# 提示：计时用同步的 perf_counter 就行，它只是读个表，不涉及等待。


async def fetch_serial(urls: list[str]) -> list[str]:
    results: list[str] = []
    for url in urls:
        result = await fake_fetch(url)
        results.append(result)
    return results


t2 = time.perf_counter()
results = asyncio.run(
    fetch_serial(["https://a.com", "https://b.com", "https://c.com"])
)
print(f"串行耗时 {time.perf_counter() - t2:.2f} 秒")
print(results)

# ============ 练习 3：gather 并发对比 ============
# TODO 3：写 async 函数 fetch_concurrent(urls)：
#   a. 用 await asyncio.gather(*(fake_fetch(u) for u in urls)) 一次并发。
#      （生成器表达式解包进 gather —— 呼应 02.3）
#   b. 计时打印「并发耗时 x.xxx 秒」（期望 ≈0.5）。
#   c. 在 main 里先串行后并发各跑一遍，最后 print 一句你的结论。
# 结论提示：串行耗时 ≈ 单次延迟 × 任务数；并发耗时 ≈ 单次延迟（等待被共享了）。


async def fetch_concurrent(urls: list[str]) -> list[str]:
    return await asyncio.gather(*(fake_fetch(u) for u in urls))


t3 = time.perf_counter()
results3 = asyncio.run(
    fetch_concurrent(["https://a.com", "https://b.com", "https://c.com"])
)
print(f"并行耗时 {time.perf_counter() - t3:.2f} 秒")
print(results3)
print("结论：串行耗时 ≈ 单次延迟 × 任务数；并发耗时 ≈ 最慢单个任务（等待被共享了）")

# ============ 练习 4（选做）：异常与超时 ============
# TODO 4：
#   a. 写 flaky_fetch(url)：抛硬币（random.random() < 0.5）决定成功或 raise TimeoutError。
#   b. 用 TaskGroup 并发 3 个，观察某个失败时整组的行为。
#   c. 用 asyncio.timeout(0.3) 包住一个 sleep(1) 的任务，捕获 TimeoutError。


async def flaky_fetch(url: str) -> str:
    """抛硬币：< 0.5 进入超时分支（sleep 1 > 限时 0.3，必超时），否则成功。"""
    if random.random() < 0.5:
        async with asyncio.timeout(0.3):  # 0.3 秒内没完成 → 抛 TimeoutError
            await asyncio.sleep(1)
    return f"{url} 的页面内容(200 OK)"


async def run_task_group(urls: list[str]) -> list[str]:
    tasks: list[asyncio.Task[str]] = []
    async with asyncio.TaskGroup() as tg:
        for url in urls:
            # create_task 只是「排班」就立刻返回，任务此刻还没跑完
            tasks.append(tg.create_task(flaky_fetch(url)))
        # 块结束前 TaskGroup 自动等待全部任务：全部成功才走到块外；
        # 有一个失败 → 取消其余任务，聚合抛 ExceptionGroup
    return [t.result() for t in tasks]  # 走到这里任务必已完成，result() 才安全


try:
    results4 = asyncio.run(
        run_task_group(["https://a.com", "https://b.com", "https://c.com"])
    )
    print(results4)
except* TimeoutError as eg:
    # TaskGroup 抛的是 ExceptionGroup（可能同时包多个 TimeoutError），
    # 普通 except TimeoutError 接不住；except* 按组内异常「类型」拆包，只抓超时这一种
    print(f"{len(eg.exceptions)} 个请求超时：{eg.exceptions}")
