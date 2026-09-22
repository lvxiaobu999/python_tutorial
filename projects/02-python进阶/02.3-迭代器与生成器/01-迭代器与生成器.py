"""迭代器与生成器：__iter__/__next__、yield、生成器表达式、yield from

迭代器是带游标的一次性取数器；生成器是「写迭代器最省事的方式」——
函数里出现 yield，调用它就得到一个生成器（能被 for 消费）。
"""

from itertools import islice


# ============ 演示 1：手写迭代器类（理解协议） ============
class Countdown:
    """用类实现迭代器协议：__iter__ 返回自己，__next__ 产出下一个。"""

    def __init__(self, start: int):
        self.current = start

    def __iter__(self) -> "Countdown":
        return self               # 迭代器自己就是迭代器

    def __next__(self) -> int:
        if self.current <= 0:
            raise StopIteration   # 取完了，for 靠这个信号正常结束
        self.current -= 1
        return self.current + 1


print(list(Countdown(3)))         # [3, 2, 1] —— for 全靠 __iter__/__next__ 工作


# ============ 演示 2：同样的功能，生成器三行搞定 ============
def countdown(start: int):
    current = start
    while current > 0:
        yield current             # 交出值并暂停，下次从这里继续
        current -= 1


print(list(countdown(3)))         # [3, 2, 1] —— 生成器自动实现了整套迭代器协议


# ============ 演示 3：无限生成器（惰性，用多少算多少） ============
def fibonacci():
    """无限产出斐波那契数：0, 1, 1, 2, 3, 5, ..."""
    a, b = 0, 1
    while True:                   # 无限循环没问题：没人要就不算
        yield a
        a, b = b, a + b


print(list(islice(fibonacci(), 10)))   # [0, 1, 1, 2, 3, 5, 8, 13, 21, 34]


# ============ 演示 4：生成器表达式 vs 列表推导式 ============
squares_list = [x * x for x in range(5)]       # 立刻算好，占内存，可反复用
squares_gen = (x * x for x in range(5))        # 惰性，一次性
print(squares_list)                             # [0, 1, 4, 9, 16]
print(squares_gen)                              # <generator object ...> 还没算
print(sum(squares_gen))                         # 30 —— sum 消费它
# print(list(squares_gen))    # [] —— 已经耗尽！生成器只能消费一次


# ============ 演示 5：yield from 展平嵌套 ============
def flatten(nested: list) :
    for item in nested:
        if isinstance(item, list):
            yield from flatten(item)   # 子生成器的产出直接转交出去
        else:
            yield item


print(list(flatten([1, [2, 3, [4, [5]]], 6])))   # [1, 2, 3, 4, 5, 6]


# ============ 练习 1：无限生成器 ============
# TODO 1：写 naturals(start=1)：无限产出 start, start+1, start+2, ...
#   然后用 islice(naturals(100), 5) 取前 5 个，期望 [100, 101, 102, 103, 104]。
#
# def naturals(start=1):
#     ...


# ============ 练习 2：流式读文件 ============
# TODO 2：写生成器 read_lines(path)，逐行产出「去掉首尾空白后的行」：
#   a. 用 with open(path, encoding="utf-8") 逐行 yield（open 本身就是逐行惰性读）。
#   b. 跳过空行。
#   c. 再写 count_keyword(path, keyword)：基于 read_lines 统计包含关键词的行数。
#   d. 自建一个几行的 txt 测试（可以复用模块 01 的 notes.txt 的思路，自建更简单）。
#
# 期望效果（举例）：
# print(count_keyword("test.txt", "python"))   # 输出包含 python 的行数


# ============ 练习 3：生成器表达式 ============
# TODO 3：一行代码（用生成器表达式 + sum）：
#   求 1~100 中所有偶数的平方和。期望结果 171700。
#
# print(sum(...))    # 在 ... 处填生成器表达式


# ============ 练习 4（选做）：管道 ============
# TODO 4：把生成器串成管道处理一组数字（来自 range(20)）：
#   第 1 段：过滤出 3 的倍数（生成器函数 evens_of / multiples_of）。
#   第 2 段：把每个数平方（生成器函数）。
#   第 3 段：sum 汇总。
# 体会：三段串联，任何时刻内存里只有一个数在流动。
