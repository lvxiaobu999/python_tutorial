"""类型注解：typing、容器类型、Optional/Union、泛型、Literal、TypedDict

注解是「写给人和工具看的类型契约」：默认不影响运行（传错类型照样能跑），
靠 pyright/mypy 在运行前检查。FastAPI 则直接读注解做运行时校验。
"""

from collections.abc import Callable, Iterable
from typing import Literal, TypedDict


# ============ 演示 1：基础注解 ============
def price(total: float, count: int) -> float:
    """参数和返回值都标清楚，IDE 才能精准补全。"""
    return total / count


def log(message: str) -> None:
    """没有返回值就写 -> None。"""
    print("[LOG]", message)


log(f"单价：{price(100, 4)}")       # 25.0
log(f"传 float 也能跑：{price(100, 2.5)}")   # 40.0 —— 注解说 count 是 int，
                                              # 传 float 运行时不报错（要靠 pyright 抓）


# ============ 演示 2：容器类型与 Union ============
type ScoreTable = dict[str, list[float]]      # 3.12+ 的 type 语句定义别名


def average(table: ScoreTable, student: str) -> float | None:
    """返回 float 或 None（找不到该学生时）——注意 | None 不等于参数可省略！"""
    scores = table.get(student)
    if scores is None:
        return None
    return sum(scores) / len(scores)


table: ScoreTable = {"小明": [90, 80], "小红": [100, 95]}
print(average(table, "小明"))        # 85.0
print(average(table, "小刚"))        # None


# ============ 演示 3：Literal 与 Callable/Iterable ============
def sort_items(items: list[int], order: Literal["asc", "desc"] = "asc") -> list[int]:
    """Literal：order 只允许这两个字符串，写错工具立刻标红。"""
    return sorted(items, reverse=order == "desc")


def apply(func: Callable[[int, int], int], a: int, b: int) -> int:
    """Callable[[参数类型们], 返回类型]：把函数当参数传。"""
    return func(a, b)


def total(nums: Iterable[int]) -> int:
    """Iterable：list/tuple/生成器都能传，比写死 list[int] 更宽容。"""
    return sum(nums)


print(sort_items([3, 1, 2], "desc"))          # [3, 2, 1]
print(apply(lambda a, b: a * b, 6, 7))        # 42
print(total(x * x for x in range(4)))         # 14 —— 生成器表达式也能传


# ============ 演示 4：泛型 ============
class Box[T]:                                  # T 是类型占位符，实例化时才确定
    def __init__(self, item: T) -> None:
        self.item = item

    def get(self) -> T:                        # 放进去什么类型，取出来就是什么类型
        return self.item


def first_of[T](items: list[T]) -> T:
    return items[0]


book_box = Box("三体")                         # 推断为 Box[str]
num_box = Box(42)                              # 推断为 Box[int]
print(book_box.get().upper())                  # 三体.upper() —— 工具知道它是 str
print(first_of([1, 2, 3]), first_of(["a", "b"]))   # 1 a —— 同一函数适配多种类型


# ============ 演示 5：TypedDict ============
class Movie(TypedDict):
    title: str
    rating: float


movie: Movie = {"title": "流浪地球", "rating": 8.0}
# movie["titel"]  # ← 键名写错，pyright 会直接标红；纯运行时则抛 KeyError


# ============ 练习 1：给无注解函数补全类型 ============
# TODO 1：为下面每个函数补全参数与返回值注解：
#   a. word_count(text) -> ??     text 是 str，返回 int
#   b. top_scores(scores) -> ??   scores 是 list[float]，返回 list[float]（前 3 名）
#   c. banner(title, width=20) -> ??   返回 None（只 print）
#   d. find_index(items, target) -> ??  items 是 list[str]，找不到返回 None
#
# def word_count(text):
#     return len(text.split())
#
# def top_scores(scores):
#     return sorted(scores, reverse=True)[:3]
#
# def banner(title, width=20):
#     print(f"{title:^{width}}")
#
# def find_index(items, target):
#     for i, item in enumerate(items):
#         if item == target:
#             return i
#     return None


# ============ 练习 2：类型别名 ============
# TODO 2：用 type 语句定义并使用：
#   a. type UserId = int，写函数 greet(uid: UserId) -> str。
#   b. type Matrix = list[list[float]]，写函数 transpose(m: Matrix) -> Matrix（转置）。
# 验证：transpose([[1, 2], [3, 4]]) 期望 [[1, 3], [2, 4]]。


# ============ 练习 3：泛型 Stack ============
# TODO 3：写泛型类 Stack[T]（后进先出栈）：
#   a. push(item: T) -> None；pop() -> T（空栈抛 IndexError）；
#   b. peek() -> T；is_empty() -> bool；__len__ -> int（呼应 02.1）。
# 验证：Stack[str] 压入 "a"、"b"，pop 出 "b"；len 为 1。


# ============ 练习 4：Literal + 静态检查 ============
# TODO 4：
#   a. 写函数 set_mode(mode: Literal["dev", "prod"]) -> None。
#   b. 先直接调用 set_mode("up")，观察：能跑？还是报错？（运行时其实能跑）
#   c. 执行 uv add --dev pyright && uv run pyright 这一行所在的文件，
#      看工具如何标红这个调用 —— 体会「注解 + 静态检查」的组合拳。
