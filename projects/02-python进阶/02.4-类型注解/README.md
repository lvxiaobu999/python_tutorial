# 02.4 类型注解

> 这一章解决「怎么让代码自己说明类型」。注解是写给人和工具看的契约：IDE 靠它补全、pyright/mypy 靠它静态查错、**FastAPI 靠它在运行时做参数校验和文档生成**。学完这章你才能看懂 FastAPI 路由函数的每一个字符。

## 知识点速查

### 1. 为什么需要类型注解

```python
def price(total, count):          # 不加注解：count 是 int 还是 str？返回什么？
    return total / count

def price(total: float, count: int) -> float:   # 加注解：一眼看懂
    return total / count
```

三个价值：① IDE 精准补全和跳转；② 静态检查工具在**运行前**发现 `price("a", 5)` 这类 bug；③ 团队协作不用翻实现。

**关键认知**：注解默认**不影响运行**——传错类型不会自动报错（`"a" * 3` 照样跑）。要真正检查需用工具：`uv add --dev pyright` 后 `uv run pyright 文件名`。FastAPI 是特例：它读取注解并在运行时校验请求参数。

### 2. 基础写法

```python
name: str = "小明"                     # 变量注解（可只声明不赋值：name: str）
age: int = 18
scores: list[float] = [92.5, 88.0]


def greet(name: str, excited: bool = False) -> str:   # 参数 + 返回值
    return f"你好 {name}{'!' if excited else '.'}"


def log(message: str) -> None:        # 没有返回值就写 -> None
    print(message)
```

### 3. 容器类型（3.9+ 直接用内置类型）

| 注解 | 含义 |
|------|------|
| `list[int]` | 整数列表 |
| `dict[str, int]` | 键是 str、值是 int 的字典 |
| `tuple[int, str]` | 固定长度：第一个 int 第二个 str |
| `tuple[int, ...]` | 不定长：任意个 int |
| `set[str]` | 字符串集合 |

> 老代码里的 `List[int]`（从 typing 导入）是历史写法，Python 3.9+ 一律用内置 `list[int]`。

### 4. Optional 与 Union：可能是多种类型

```python
from typing import Optional, Union

def find_user(user_id: int) -> str | None:      # 3.10+ 优先用 | 写法
    ...                                          # 找到返回名字，找不到返回 None

# 三种等价写法：
# Optional[str] == Union[str, None] == str | None
def parse(value: int | str) -> int:             # 接受 int 或 str
    return int(value)
```

⚠️ 头号误区：`Optional[str]` 的意思是「str 或 None」，**不是「参数可以不传」**。参数可不可以省略由**默认值**决定：`def f(x: int = 0)`。且 `x: int | None = None` 才表示「默认 None，传就得是 int 或 None」。

### 5. 别名、Literal、Final

```python
# 类型别名：给复杂类型起短名（3.12+ 的 type 语句）
type UserId = int
type ScoreTable = dict[str, list[float]]

def get_name(uid: UserId) -> str: ...


from typing import Literal, Final

def sort_items(items: list[int], order: Literal["asc", "desc"] = "asc") -> list[int]:
    # Literal：值只能是这几个字符串，写错工具立刻标红
    ...

MAX_RETRY: Final = 3        # Final：约定不再改的常量
```

### 6. 鸭子类型的注解（collections.abc）

```python
from collections.abc import Callable, Iterable, Sequence, Mapping

def apply(func: Callable[[int, int], int], a: int, b: int) -> int:   # 接收函数
    return func(a, b)

def total(nums: Iterable[int]) -> int:       # 任何能遍历的都行：list/生成器/set...
    return sum(nums)

def first(items: Sequence[str]) -> str:      # 有序可下标：list/tuple/str
    return items[0]

def lookup(table: Mapping[str, int], key: str) -> int:   # 类似 dict 的只读视图
    return table[key]
```

用 `Iterable[int]` 而不是 `list[int]`：前者接受面更广（生成器也能传），而且不强制调用方先转 list——**参数宽松、返回精确**是好习惯。

### 7. 泛型：写一次类型，处处套用

```python
def first_item(items: list[int]) -> int: ...        # 只能用于 int 列表

# 3.12+ 语法：T 是类型占位符，调用时才确定
def first_of[T](items: list[T]) -> T:               # 传 list[str] → T 就是 str
    return items[0]


class Box[T]:                                        # 泛型容器类
    def __init__(self, item: T) -> None:
        self.item = item

    def get(self) -> T:
        return self.item


box = Box("hello")          # 推断为 Box[str]
name: str = box.get()       # get() 返回 str，工具完全知道
```

老代码用 `TypeVar` + `Generic[T]`（from typing import TypeVar, Generic），效果相同，见到要认识。

### 8. TypedDict：给固定结构的字典上类型

```python
from typing import TypedDict

class Movie(TypedDict):
    title: str
    rating: float


movie: Movie = {"title": "流浪地球", "rating": 8.0}
# movie["titel"]  ← pyright 直接标红，键名写错当场发现
```

LangGraph 的 State（模块 08）就用 TypedDict 定义，先混个脸熟。

## 易错点

- 以为注解会运行时强制检查——`def f(x: int)` 传 `"abc"` 照样跑，想检查要跑 pyright/mypy。
- 把 `Optional[int]` 当成「可省略的参数」——可省略靠默认值 `x: int = 0`。
- 写裸的 `list`、`dict` 不带参数（`list` 能匹配任何列表，信息量为零，不如 `list[int]`）。
- 还在用 `typing.List` / `typing.Dict` 老写法——3.9+ 直接 `list[int]` / `dict[str, int]`。
- `Any` 满天飞——`Any` 等于放弃检查，实在没辙再用（如和 json 打交道时逐步收窄类型）。
- 注解了却从不跑检查工具，注解就只是注释。

## 进阶提示

- 本项目加检查工具：`uv add --dev pyright` → `uv run pyright`，让它进日常工作流。
- `cast(str, value)`：类型收窄的「信任断言」，配合 json 解析用。
- `if TYPE_CHECKING:` 里放只给工具看的 import，避免运行时循环导入。
- Python 3.12 之前的老项目用 `TypeVar("T")` + `Generic[T]`；新代码用 `[T]` 新语法。
- 学完这章可以回头看 FastAPI 官网第一段示例——`def read_item(item_id: int)` 里的注解就是校验器。

## 学习顺序与练习

先跑演示文件确认能运行（注解不改变行为），再完成 TODO；练完立刻装 pyright 扫一遍自己写的代码，看看能抓出几个隐患。

基础 TODO（见 `01-类型注解.py`）：
1. 给四个无注解函数补全类型（含 `-> None`、容器、`int | None`）。
2. 用 `type` 语句定义 `UserId`、`ScoreTable` 别名并用在函数签名里。
3. 实现 `Box[T]` 泛型盒子：`put`/`get`，并体会「放入 str 取出必是 str」。
4. 给排序函数加 `Literal["asc", "desc"]`，故意传 `"up"` 看看 pyright 是否报错（运行时不报！）。
