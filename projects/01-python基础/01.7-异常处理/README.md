# 01.7 异常处理

> 这一章解决「程序出错时怎么办」。让程序在遇到坏输入、缺文件、余额不足等情况时不崩溃，而是给出可读的提示并继续运行。

## 知识点速查

### 1. 异常是什么

异常（Exception）表示运行时无法正常完成的情况。`int("abc")` 抛 `ValueError`，`10 / 0` 抛 `ZeroDivisionError`。异常不处理时程序立即中断，并打印 traceback（堆栈回溯，标出出错的那一行和调用链）。

### 2. try / except / else / finally 完整结构

```python
try:
    number = int("18")            # 可能出错的代码
except ValueError as error:       # 出错时执行，error 是异常对象
    print("出错：", error)
else:
    print("成功：", number)        # try 没出错才执行
finally:
    print("无论如何都执行")        # 收尾：关文件、释放资源
```

执行顺序速记：

| 情况 | 执行顺序 |
|------|----------|
| try 没出错 | try → else → finally |
| try 出错且被捕获 | try（中断处）→ except → finally |
| try 出错但没被捕获 | try（中断处）→ finally 仍执行 → 异常继续向上抛 |

要点：
- `else` 的意义：把「可能出错的代码」和「依赖其结果的后续代码」分开，避免 except 意外吞掉后续代码的异常。
- `finally` 用于清理资源，即使 except 里又出了新异常，它也会执行。
- `as error` 把异常对象存进变量，`str(error)` 就是错误消息。

### 3. 捕获方式速查表

| 写法 | 含义 | 建议 |
|------|------|------|
| `except ValueError:` | 捕获指定异常 | ✅ 首选，提示最具体 |
| `except (ValueError, TypeError):` | 捕获多种，同一套处理 | ✅ 合理 |
| `except Exception as e:` | 捕获几乎所有异常 | ⚠️ 只在程序顶层兜底用 |
| `except:` | 裸捕获，连 Ctrl+C 都吞 | ❌ 禁用，会掩盖真正的 bug |
| 多个 except 分支 | 从上到下匹配，命中一个就跳过其余 | 子类要放在父类前面 |

注意：`except Exception` 若写在最前面，后面的分支永远不会执行。

### 4. 常见异常速查表

| 异常 | 什么时候抛出 | 典型例子 |
|------|--------------|----------|
| `ValueError` | 类型对但值不合适 | `int("abc")` |
| `TypeError` | 类型不支持该操作 | `"a" + 1`、`[1, 2]["x"]` |
| `IndexError` | 序列下标越界 | `[1, 2][5]` |
| `KeyError` | 字典键不存在 | `{"a": 1}["b"]` |
| `ZeroDivisionError` | 除数为 0 | `10 / 0` |
| `FileNotFoundError` | 文件路径不存在 | `open("不存在.txt")` |
| `AttributeError` | 对象没有该属性/方法 | `"abc".push()` |
| `NameError` | 使用未定义的变量 | `print(未定义)` |

区分 `ValueError` 和 `TypeError`：`int("abc")` 是值错（字符串能转 int，但内容不行）；`int([1, 2])` 是类型错（列表根本不能转）。根据异常类型给用户具体提示，比统一打印「出错了」更容易排查。

### 5. raise：主动抛出异常

```python
def parse_age(value):
    age = int(value)
    if age < 0:
        raise ValueError(f"年龄不能为负数，收到：{age}")
    return age
```

- `raise` 后面跟异常实例（或类名，会自动实例化），用于「输入不满足业务规则」时主动报错。
- 在 except 里裸写 `raise` 表示「记录后继续上抛」，保留原始 traceback。

### 6. 自定义异常

```python
class OutOfStockError(Exception):
    """库存不足时抛出。继承 Exception 就成为一个可捕获的异常类。"""

    def __init__(self, stock, want):
        super().__init__(f"库存不足：现有 {stock}，需要 {want}")
        self.stock = stock      # 异常对象上可以携带业务数据
        self.want = want


def place_order(stock, want):
    if want > stock:
        raise OutOfStockError(stock, want)
    return stock - want


try:
    place_order(3, 5)
except OutOfStockError as e:
    print("下单失败：", e)
    print("还差：", e.want - e.stock)
```

自定义异常的价值：调用方能用 `except OutOfStockError` 精确捕获业务错误，不会误捕其他异常；异常对象上还能带业务字段供处理方读取。异常消息应说明发生了什么以及如何修正。

### 7. 异常链：raise ... from ...

```python
import json

try:
    config = json.loads(raw_text)
except json.JSONDecodeError as error:
    raise ValueError("配置文件格式不合法") from error
```

`from error` 保留原始异常，traceback 会显示「The above exception was the direct cause of...」，方便定位根因；不带 from 则显示「During handling of the above exception, another exception occurred」。

### 8. 两种防御风格：EAFP vs LBYL

| 风格 | 全称 | 写法 | 说明 |
|------|------|------|------|
| EAFP | 好绕恕比许可更容易 | `try: v = d["k"] except KeyError: ...` | ✅ 更 Pythonic |
| LBYL | 先检查再行动 | `if "k" in d: v = d["k"]` | 检查和访问之间数据可能变化 |

## 易错点

- 裸 `except:` 吞掉一切异常，出 bug 时无从排查；永远写具体异常类型。
- `except` 离错误源太远，中间代码的异常会被误捕。
- `finally` 里写 `return` 会吞掉异常和返回值，别这么用。
- `else` 不是 `if/else` 的 else，它的含义是「try 成功后才执行」。
- 自定义异常忘记继承 `Exception`，raise 时会报 TypeError。
- 多个 except 分支按顺序匹配，父类写前面会挡住后面的子类分支。

## 进阶提示

- 顶层兜底：程序入口用 `try ... except Exception: logging.exception("出错了")` 记录完整 traceback，避免服务直接崩溃。`logging.exception()` 只能在 except 块里调用，会自动带上 traceback。
- 装饰器 + 异常 = 重试装饰器：捕获异常 → 记录 → sleep → 重试，最多 N 次，超限后 `raise` 上抛（结合 01.4 的装饰器知识）。
- 异常体系设计：先定业务基类如 `PaymentError(Exception)`，再派生 `InsufficientBalanceError`、`AccountFrozenError` 等子类，调用方捕获基类即可覆盖全部子类。

## 学习顺序与练习

先完成示例中的年龄解析，再做健壮计算器、文件批处理、自定义异常体系和重试装饰器；面试回顾重点是异常执行顺序、具体捕获和异常链。

基础 TODO（见 `01-异常与自定义.py`）：
1. 安全地读取两个数字并做除法：用 `int()` 转换输入，分别处理 `ValueError`（转换失败）和 `ZeroDivisionError`（除数为 0）。
2. 读取列表下标并取元素：处理转换失败（`ValueError`）和 `IndexError`（下标越界）两种情况，给出不同提示。
3. 为余额不足定义 `InsufficientBalanceError`，在转账函数中抛出，捕获后打印包含余额和转账额的提示。
