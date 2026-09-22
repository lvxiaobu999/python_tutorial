# 02.2 装饰器与闭包

> 这一章解决「如何给函数增强功能而不改动它」。装饰器 = 闭包的应用：把「计时、缓存、重试、注册路由」这类横切逻辑从业务代码里抽出来。FastAPI 的 `@app.get(...)`、pytest 的 `@pytest.fixture`、dataclass 的 `@dataclass` 全是装饰器——这是阅读一切框架代码的基础。

## 知识点速查

### 1. 闭包是什么

内层函数引用了外层函数的变量，并且外层函数把这个内层函数返回出去——被引用的变量就和函数一起「被打包」带走了。

```python
def make_counter():
    count = 0                 # 这个变量被闭包「记住」

    def counter():
        nonlocal count        # 要修改外层变量必须声明 nonlocal
        count += 1
        return count

    return counter            # 返回的是函数本身（不带括号！）

c = make_counter()
print(c(), c(), c())          # 1 2 3 —— count 不随 make_counter 结束而消失
```

- `counter` 能访问已经**返回了的** `make_counter` 的局部变量，这就是闭包。
- 想修改闭包变量要 `nonlocal`；只读不需要。
- `c.__closure__` 可以看到闭包捕获的单元格（cell）。
- 闭包的价值：函数带上了「出厂设置」（环境数据），不需要全局变量。

### 2. 闭包经典坑：late binding（晚绑定）

```python
funcs = [lambda: i for i in range(3)]
print([f() for f in funcs])        # [2, 2, 2]，不是 [0, 1, 2]！

funcs = [lambda i=i: i for i in range(3)]   # 用默认参数立刻"烙"住当前值
print([f() for f in funcs])        # [0, 1, 2]
```

原因：三个 lambda 引用的是**同一个变量 i**，调用时 `i` 已经是循环结束后的 2。用 `i=i` 默认参数在定义瞬间拷贝一份。

### 3. 装饰器本质

```python
def decorator(func):
    def wrapper(*args, **kwargs):          # *args/**kwargs 接住任意参数（呼应 01.4）
        print("前置动作")
        result = func(*args, **kwargs)     # 调用原函数
        print("后置动作")
        return result
    return wrapper


@decorator
def hello(name):
    return f"你好，{name}"


# @decorator 完全等价于：hello = decorator(hello)
print(hello("小明"))
```

- 装饰器就是「接收函数、返回新函数」的高阶函数，`@x` 只是语法糖。
- 装饰发生在 `def` 执行的那一刻（import 时），不是调用时。
- `wrapper` 里必须 `return func(...)` 的结果，否则被装饰的函数返回值丢了。

### 4. 标准模板：functools.wraps + 带参数的装饰器

```python
import functools


def repeat(times):                          # 第一层：收装饰器参数
    def decorator(func):                    # 第二层：收被装饰函数
        @functools.wraps(func)              # 把原函数的 __name__/__doc__ 抄给 wrapper
        def wrapper(*args, **kwargs):       # 第三层：实际执行
            result = None
            for _ in range(times):
                result = func(*args, **kwargs)
            return result
        return wrapper
    return decorator


@repeat(times=3)
def ping():
    print("pong")

# 等价于 ping = repeat(times=3)(ping)
ping()
print(ping.__name__)        # ping —— 没有 @wraps 这里会是 wrapper
```

- 带参数的装饰器 = 三层函数，`@repeat(3)` 与 `@repeat` 的区别就是「多了一层括号」。
- `@functools.wraps(func)` 几乎必加：不加的话函数名、文档字符串、报错堆栈全显示 `wrapper`，调试会很痛苦。

### 5. 常用内置装饰器速查表

| 装饰器 | 作用 | 所属 |
|--------|------|------|
| `@functools.wraps(func)` | 保留被装饰函数的元信息 | functools |
| `@functools.lru_cache(maxsize=...)` | 按参数缓存结果，重复调用不再计算 | functools |
| `@functools.cache` | lru_cache 的无上限版（3.9+） | functools |
| `@staticmethod` / `@classmethod` | 静态/类方法（02.1） | 内置 |
| `@property` | 方法伪装成属性（02.1） | 内置 |
| `@dataclass` | 自动生成 `__init__` 等（02.1） | dataclasses |
| `@pytest.mark.parametrize` | 参数化测试（02.7） | pytest |

### 6. 多个装饰器的顺序（洋葱模型）

```python
@a
@b
def f(): ...
# 等价于 f = a(b(f))：装饰从下往上（离函数近的先包），执行时从上往下（外层先进入）
```

## 易错点

- `return counter` 写成 `return counter()`——前者返回函数（对），后者立刻执行并返回结果（错）。
- wrapper 忘记 `return func(...)`，被装饰函数的返回值变成 None。
- 忘记 `@functools.wraps`：`f.__name__` 变成 `wrapper`，多个被装饰函数的堆栈难以区分。
- `@repeat` 与 `@repeat(3)` 混淆：定义了三层却用 `@repeat`，会把**函数本身**当成装饰器参数。
- 闭包晚绑定：循环里建闭包/lambda 全部拿到最后一个值。
- 在装饰器本体（第二层）里写执行逻辑——import 时就执行了，通常不是你想要的。

## 进阶提示

- **重试装饰器**：wrapper 里 `try/except` + `time.sleep` + 最多 N 次，超限 `raise` 上抛（与 01.7 异常链配合），这是爬虫/调 API 的实用件。
- **注册表装饰器**：装饰器把函数存进字典 `REGISTRY[name] = func`，之后按名字调用——FastAPI 的 `@app.get("/path")` 注册路由就是这个原理。
- 类也能当装饰器（实现 `__call__`，见 02.1），`@dataclass` 本身就是类装饰器。
- 装饰器也可以叠在类的方法上，例如给 API 层的每个方法统一加日志、计时、鉴权。

## 学习顺序与练习

先跑通演示（counter 闭包、repeat 装饰器），再按顺序完成 TODO；练 2 完成后回头看 FastAPI 文档里的 `@app.get`，应该能大致看懂了。

基础 TODO（见 `01-闭包与装饰器.py`）：
1. `make_multiplier(n)` 闭包：返回把输入乘以 n 的函数。
2. `@timer` 装饰器：用 `time.perf_counter` 打印函数名与耗时（记得 `@wraps` 和返回值）。
3. `@repeat(n)` 带参数装饰器：让函数连执行 n 次。
4. 选做：`@lru_cache` 加速斐波那契，对比 35 项的耗时差异。
