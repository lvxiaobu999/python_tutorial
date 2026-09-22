# 02.1 面向对象

> 这一章解决「如何用类组织代码」。数据和操作数据的方法打包在一起，通过继承复用、通过魔术方法让自定义对象像内置类型一样好用。FastAPI 的 Pydantic 模型、LangChain 的组件全是类——读懂类，才能读懂框架。

## 知识点速查

### 1. 类与实例

类（class）是图纸，实例（instance）是照图纸造出来的具体对象。

```python
class Dog:
    species = "犬科"            # 类属性：所有实例共享，只有一份

    def __init__(self, name):   # 构造方法：Dog("旺财") 时自动调用
        self.name = name        # 实例属性：每个实例各有一份

    def bark(self):             # 实例方法：第一个参数永远是 self
        return f"{self.name}：汪！"


dog_a = Dog("旺财")
dog_b = Dog("小黑")
print(dog_a.name, dog_b.name)       # 旺财 小黑 —— 各自独立
print(dog_a.species is dog_b.species)  # True —— 共享同一个类属性
```

- `self` 就是「这个实例自己」，调用时不用传：`dog_a.bark()` 等价于 `Dog.bark(dog_a)`。
- 找属性顺序：先找实例自己的，找不到再找类的。所以**可变类属性是共享的**，往里 append 会影响所有实例（见易错点）。

### 2. 三种方法速查表

| 写法 | 第一个参数 | 能访问什么 | 什么时候用 |
|------|-----------|-----------|-----------|
| 普通方法 | `self` | 实例 + 类 | 需要读/改实例数据（最常用） |
| `@classmethod` | `cls` | 只有类 | 替代构造器、工厂方法 |
| `@staticmethod` | 无 | 都不直接访问 | 和类相关的纯函数，放类里只是归档 |

```python
class Date:
    def __init__(self, year, month, day):
        self.year, self.month, self.day = year, month, day

    @classmethod
    def from_string(cls, text):          # 替代构造器："2026-09-21" → Date
        year, month, day = text.split("-")
        return cls(int(year), int(month), int(day))

    @staticmethod
    def is_leap(year):                   # 不需要实例数据，纯计算
        return year % 4 == 0 and (year % 100 != 0 or year % 400 == 0)
```

### 3. 继承与 super()

```python
class Animal:                       # 父类（基类）
    def __init__(self, name):
        self.name = name

    def speak(self):
        return f"{self.name}发出了声音"


class Dog(Animal):                  # Dog「是一种」Animal
    def __init__(self, name, breed):
        super().__init__(name)       # 委托父类初始化，别重复抄父类代码
        self.breed = breed

    def speak(self):                 # 重写（override）父类方法
        return f"{self.name}：汪！"
```

- `isinstance(dog, Animal)` 为 True：子类实例也是父类实例。
- 方法查找沿继承链向上找，找到第一个为止；`super()` 用来显式调用父类版本。
- 判断该不该继承：能说出「B 是一种 A」就用继承；只是「B 用到了 A」用组合（把 A 当属性），别滥用继承。

### 4. 多态与鸭子类型

```python
animals = [Dog("旺财"), Cat("咪咪")]
for a in animals:
    print(a.speak())     # 同一行调用，各自执行自己的版本 —— 多态
```

Python 的多态**不检查类型，只检查行为**：对象只要有 `speak()` 方法就能放进上面循环，哪怕它和 Animal 毫无继承关系。这叫鸭子类型（「走起来像鸭子、叫起来像鸭子，那就是鸭子」）。所以 Python 里接口约束很宽松，靠的是约定和文档。

### 5. 魔术方法速查表

魔术方法（dunder method）是 `__xx__` 形式的特殊方法，Python 在特定语法下自动调用。

| 魔术方法 | 触发时机 | 等价写法 |
|----------|----------|----------|
| `__init__` | `ClassName()` 创建实例 | — |
| `__repr__` | 调试输出、容器里显示 | `repr(obj)`、交互式直接敲变量名 |
| `__str__` | 给用户看的输出 | `print(obj)`、`str(obj)` |
| `__eq__` | 判断相等 | `a == b` |
| `__lt__` | 小于比较 | `a < b`（有了它对象才能 `sorted`） |
| `__add__` | 加法 | `a + b` |
| `__len__` | 取长度 | `len(obj)` |
| `__getitem__` | 下标访问 | `obj[i]`（有了它对象就能被 `for` 遍历） |
| `__contains__` | 成员判断 | `x in obj` |
| `__call__` | 把实例当函数调 | `obj(...)` |
| `__enter__` / `__exit__` | `with` 上下文管理（01.5 的 `with open(...)` 就是它） | `with obj:` |

```python
class Money:
    def __init__(self, yuan):
        self.yuan = yuan

    def __repr__(self):                 # 目标：开发者一眼看懂怎么再造一个
        return f"Money({self.yuan})"

    def __eq__(self, other):
        return isinstance(other, Money) and self.yuan == other.yuan

    def __add__(self, other):
        return Money(self.yuan + other.yuan)


print(Money(8) + Money(2))   # Money(10) —— + 触发 __add__，print 触发 __repr__
print(Money(8) == Money(8))  # True —— 不写 __eq__ 时比较的是内存地址
```

`__repr__` 与 `__str__`：只写一个就写 `__repr__`（`print` 找不到 `__str__` 时会退回它）。惯例：`__repr__` 输出「类名(能重建实例的参数)」。

### 6. property：把方法伪装成属性

```python
class Circle:
    def __init__(self, radius):
        self._radius = radius        # 下划线开头 = 约定俗成的「内部变量，别直接碰」

    @property
    def radius(self):                # 读取 c.radius 走这里
        return self._radius

    @radius.setter
    def radius(self, value):         # 赋值 c.radius = x 走这里，顺便做校验
        if value <= 0:
            raise ValueError("半径必须大于 0")
        self._radius = value
```

价值：调用方写 `c.radius` 像访问属性一样简洁，而你依然能塞进校验逻辑——这就是 Pydantic 字段校验的雏形。

### 7. dataclass：自动生成样板代码

```python
from dataclasses import dataclass, field

@dataclass
class Book:
    title: str
    price: float
    tags: list[str] = field(default_factory=list)  # 可变默认值必须用 default_factory


book = Book("Python教程", 59.9)
print(book)                    # Book(title='Python教程', price=59.9, tags=[])
print(book == Book("Python教程", 59.9))  # True —— 自动生成了 __init__、__repr__、__eq__
```

一个 `@dataclass` 顶掉 `__init__` + `__repr__` + `__eq__` 三段样板。**FastAPI 的请求/响应模型（Pydantic）就是加强版 dataclass**：多了运行时类型校验和序列化。注意 `field(default_factory=list)`：直接写 `tags: list[str] = []` 会报错（所有实例会共享同一个列表，Python 直接禁止了这种写法）。

## 易错点

- **可变类属性**：`class C: items = []` 然后实例往 `self.items` append——所有实例共享同一个列表。实例自己的可变数据必须在 `__init__` 里 `self.items = []`。
- 子类 `__init__` 忘记 `super().__init__(...)`，父类属性没被初始化，后续方法用到时报 `AttributeError`。
- 实例方法第一个参数忘写 `self`，调用时报参数数量不匹配。
- dataclass 的可变默认值写 `= []` / `= {}`，直接报错；要 `field(default_factory=...)`。
- `__eq__` 忘记写，`==` 比较的是两个对象是不是同一个（内存地址），内容相同也返回 False。
- 到处随意 `obj.anything = 1` 动态加属性——语法允许但难以维护，约定属性都在 `__init__` 里声明。

## 进阶提示

- 抽象基类：`class Shape(ABC)` + `@abstractmethod` 强制子类实现某方法，不实现就不能实例化——鸭子类型太自由时用它立规矩。
- `@dataclass(frozen=True)` 生成不可变对象（赋值报错），适合当配置、常量；`slots=True` 更省内存。
- Mixin 模式：小功能类（如 `ToJsonMixin`）多个继承拼装，比单一大父类灵活。
- 阅读框架源码时先看类的 `__init__` 和魔术方法，就能猜到这个类「怎么创建、怎么被使用」。

## 学习顺序与练习

先跑通两个练习文件的演示部分（`BankAccount` 和 `Vector2D`），再完成 TODO；这一章建议分两天：第一天类/继承/多态（`01-类与继承.py`），第二天魔术方法/property/dataclass（`02-魔术方法与dataclass.py`）。

基础 TODO（见两个练习文件末尾）：
1. `Student` 类：实例属性 + 实例方法 `average()` + 类属性统计创建个数。
2. `Animal → Dog/Cat` 继承与多态：循环里同一个调用，不同输出。
3. `Date.from_string` 类方法替代构造器。
4. `Vector2D` 魔术方法：`+`、`==`、`abs()`（向量长度）、`repr`。
5. `Playlist` 支持 `len()`、下标、`for` 遍历、`in` 判断。
6. `Temperature` 用 `@property` + setter 校验温度不低于绝对零度。
7. 用 `@dataclass` 重写 `Book`（含 `tags` 列表默认值）。
