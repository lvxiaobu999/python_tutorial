"""装饰器与闭包：闭包、@decorator、functools.wraps、带参数装饰器

闭包 = 内层函数带走外层函数的变量；装饰器 = 用闭包包装函数，在不改原函数的
前提下加功能。@x 只是 f = x(f) 的语法糖。
"""

import functools
import time


# ============ 演示 1：闭包 ============
def make_counter():
    count = 0

    def counter():
        nonlocal count       # 要「修改」闭包变量必须 nonlocal；只读不用
        count += 1
        return count

    return counter           # 返回函数本身，不是 counter()


counter_a = make_counter()
counter_b = make_counter()   # 两个计数器各自独立，互不干扰
print(counter_a(), counter_a(), counter_a())   # 1 2 3
print(counter_b())                              # 1
print(counter_a.__closure__)  # (<cell ...>) —— 闭包捕获的变量就存在这里


# ============ 演示 2：装饰器 ============
def log_call(func):
    @functools.wraps(func)   # 把原函数的名字、文档抄给 wrapper
    def wrapper(*args, **kwargs):
        print(f"[LOG] 调用 {func.__name__}，参数：{args}, {kwargs}")
        result = func(*args, **kwargs)   # 一定要 return，否则原函数返回值丢了
        print(f"[LOG] {func.__name__} 返回：{result}")
        return result

    return wrapper


@log_call
def add(a, b=0):
    """两数相加。"""
    return a + b


print(add(3, b=4))           # 前后多出两行日志，功能没变
print(add.__name__, add.__doc__)   # add 两数相加。 —— @wraps 保住了元信息


# ============ 演示 3：带参数的装饰器（三层） ============
def repeat(times):
    def decorator(func):                 # 第 1 层收装饰器参数，第 2 层收函数
        @functools.wraps(func)
        def wrapper(*args, **kwargs):    # 第 3 层才真正执行
            result = None
            for _ in range(times):
                result = func(*args, **kwargs)
            return result

        return wrapper

    return decorator


@repeat(times=3)
def ping():
    print("pong")


ping()                       # 连打三次 pong


# ============ 演示 4：lru_cache 缓存 ============
@functools.lru_cache(maxsize=None)   # 相同参数的调用直接返回缓存，不再重算
def slow_square(n):
    time.sleep(0.1)         # 假装计算很慢
    return n * n


start = time.perf_counter()
slow_square(9)
slow_square(9)              # 第二次命中缓存，几乎不花时间
print(f"两次 slow_square(9) 共耗时 {time.perf_counter() - start:.3f} 秒（本应 0.2 秒）")


# ============ 练习 1：闭包工厂 ============
def make_multiplier(n):
    """TODO 1：返回一个函数 f(x)，调用 f(x) 返回 x * n。

    提示：函数体只需要 def inner(x): return x * n，然后 return inner。
    """
    raise NotImplementedError("TODO 1：删除这行，按 docstring 完成")


# 完成后取消注释验证：
# double = make_multiplier(2)
# triple = make_multiplier(3)
# print(double(5), triple(5))    # 期望 10 15


# ============ 练习 2：@timer 装饰器 ============
# TODO 2：写 timer 装饰器：
#   a. 用 time.perf_counter() 记录调用前后时刻（比 time.time() 更适合测耗时）。
#   b. 打印「函数 xxx 耗时 x.xxx 秒」。
#   c. 必须：@functools.wraps + return 结果，两者缺一不可。
#
# 完成后用它装饰下面的 slow_sum 并调用：
#
# @timer
# def slow_sum(n):
#     time.sleep(0.3)
#     return sum(range(n))
#
# print(slow_sum(10_000))        # 先打印耗时，再打印 49995000


# ============ 练习 3：带参数的重试装饰器 ============
# TODO 3：写 retry(times) 装饰器（结合 01.7 异常）：
#   a. 三层结构，参照演示 3。
#   b. wrapper 里 try/except Exception：失败打印第几次重试，最多重试 times 次。
#   c. 全部失败后 raise（把最后一个异常原样上抛）。
#
# 用下面的函数测试（前两次抛错，第三次成功）：
#
# attempts = {"n": 0}
#
# @retry(times=3)
# def flaky():
#     attempts["n"] += 1
#     if attempts["n"] < 3:
#         raise ConnectionError(f"第 {attempts['n']} 次失败")
#     return "成功"
#
# print(flaky())                 # 期望看到两次重试日志后输出 成功


# ============ 练习 4（选做）：lru_cache 斐波那契 ============
# TODO 4：
#   a. 写普通递归 fib(n)，打印 fib(32) 的耗时。
#   b. 加上 @functools.lru_cache 再测一次，对比耗时。
#   c. 想一想：为什么递归 + 缓存会快这么多？（fib(n) 被重复算了多少次？）
