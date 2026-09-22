# 02.3 迭代器与生成器

> 这一章解决「如何处理一串数据而不把它全装进内存」。for 循环背后是迭代器协议；生成器用 `yield` 让函数「边产数据边被消费」，是流式处理大文件、无限序列和 LangChain 流式输出的基础。

## 知识点速查

### 1. 可迭代对象 vs 迭代器

| 概念 | 需要实现 | 怎么理解 |
|------|----------|----------|
| 可迭代对象 Iterable | `__iter__` | 能被 for 遍历的东西（list、str、dict、文件对象…） |
| 迭代器 Iterator | `__iter__` + `__next__` | 带游标的一次性取数器，负责「下一个是谁」 |

```python
fruits = ["苹果", "香蕉"]     # list 是可迭代对象
it = iter(fruits)            # iter()：从可迭代对象拿到一个迭代器（游标归零）
print(next(it))              # 苹果 —— next()：取下一个
print(next(it))              # 香蕉
next(it)                     # 取空了 → 抛 StopIteration（for 会捕获它然后正常结束）
```

### 2. for 循环的本质

```python
for x in fruits: ...
# 大致等价于：
it = iter(fruits)
while True:
    try:
        x = next(it)
    except StopIteration:
        break
    ...  # 循环体
```

for 不关心你是什么类型，只要能给迭代器它就能遍历——这也是 02.1 鸭子类型的体现。

### 3. 生成器函数：yield

函数体里出现 `yield`，它就成了生成器函数；**调用它不执行任何代码**，而是返回一个生成器（也是一种迭代器）。每次 `next` 执行到 `yield` 处暂停并交出值，下次从暂停处继续。

```python
def countdown(n):
    print("开始倒数")        # 第一次 next 才会执行（惰性）
    while n > 0:
        yield n             # 在这里暂停，把 n 交出去
        n -= 1              # 下次被唤醒从这行继续


gen = countdown(3)          # 没有任何输出！函数体一行都没跑
print(next(gen))            # 打印「开始倒数」，返回 3
print(next(gen))            # 返回 2（从 n -= 1 继续执行到 yield n）
for left in gen:            # 剩下的 1 被 for 消费
    print(left)
```

记忆法：`yield` = 「交出一件产品并就地睡着，直到有人再叫我」。这与 `return`（直接结束）最大的区别：**生成器记住了执行位置和所有局部变量**。

### 4. 生成器表达式 vs 列表推导式

```python
squares_list = [x * x for x in range(5)]      # 立刻算出整个列表：[0, 1, 4, 9, 16]
squares_gen  = (x * x for x in range(5))      # 生成器：一个都没算，要一个算一个

print(sum(x * x for x in range(10 ** 8)))     # 作唯一参数时括号可省，1亿个数不占内存
```

| | 列表推导式 `[...]` | 生成器表达式 `(...)` |
|--|--------------------|----------------------|
| 内存 | 立刻占满（全部数据） | 几乎不占（一次一个） |
| 能否重复遍历 | 能 | 不能（一次性） |
| 能否下标访问 | 能 | 不能 |
| 适用场景 | 数据小、要反复用 | 数据大 / 只消费一次 / 流式 |

### 5. yield from：委托子生成器

```python
def flatten(nested):
    for item in nested:
        if isinstance(item, list):
            yield from flatten(item)   # 把子生成器的产出直接转交
        else:
            yield item


print(list(flatten([1, [2, 3, [4]], 5])))   # [1, 2, 3, 4, 5]
```

### 6. itertools 常用工具速查表

```python
from itertools import count, cycle, chain, islice, product, groupby
```

| 函数 | 作用 | 例子 |
|------|------|------|
| `count(10)` | 无限计数 10, 11, 12… | 配合 islice 用 |
| `cycle("AB")` | 无限循环 A, B, A, B… | 轮询场景 |
| `chain(a, b)` | 把多个可迭代对象接起来 | `chain([1,2], [3])` → 1,2,3 |
| `islice(gen, 5)` | 给无限流「切片」取前 5 个 | `islice(count(), 3)` → 0,1,2 |
| `product(a, b)` | 笛卡尔积 | `product("AB", "12")` → A1,A2,B1,B2 |
| `groupby(data, key)` | 相邻分组（要先排序） | 按首字母分组名单 |

## 易错点

- **生成器是一次性的**：耗尽后再 for 一次得到空序列（它不会重置，`iter(生成器)` 返回的还是它自己）。要重复使用就再造一个，或干脆用 list。
- 调用生成器函数（`countdown(3)`）什么都不执行，忘了消费它，或者打印它看到一个 `generator object`——都说明你还没遍历它。
- 生成器里的 `return value` 不是返回值给调用方，而是结束生成并把 value 放进 `StopIteration`（知道即可，别依赖）。
- 生成器表达式当**唯一实参**时可省外层括号：`sum(x for x in ...)`；多于一个参数就必须括号。
- `groupby` 只对**相邻**元素分组，数据没先按 key 排序会得到意想不到的分组。

## 进阶提示

- **流式处理大文件**：`for line in open(...)` 本身就是迭代器逐行读，几个 GB 的日志也能统计而不爆内存。
- **生成器管道**：读一行 → 过滤（生成器）→ 清洗（生成器）→ 汇总，每段都是惰性的，全程只有一行数据在内存里——这是数据处理的经典架构。
- LangChain / FastAPI 的**流式输出**（打字机效果）底层就是「每生成一小段就 yield 出去」，模块 05/06 会直接用到。
- 想给生成器「喂数据」可以了解 `gen.send(value)`（协程的雏形，asyncio 的思想源头）。

## 学习顺序与练习

先跑演示（countdown、flatten），重点盯着「哪一行什么时候执行」；再完成 TODO。练习 2 做完建议把文件改成 10 万行再跑一遍，体会流式处理的优势。

基础 TODO（见 `01-迭代器与生成器.py`）：
1. `fib()` 无限斐波那契生成器，配 `itertools.islice` 取前 10 项。
2. `read_lines(path)` 生成器逐行读文件，统计包含关键词的行数（流式，不 `read()` 整个文件）。
3. 一行生成器表达式：求 1~100 中所有偶数的平方和。
4. 选做：`flatten` 换成你自己实现一遍 `yield from` 版，再写一个不带 `yield from` 的递归版对比。
