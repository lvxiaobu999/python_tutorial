"""面向对象（二）：魔术方法、property、dataclass

魔术方法让自定义对象支持 +、==、len()、下标、for 等内置语法；
property 把「带校验的赋值」伪装成普通属性；dataclass 一行顶三段样板代码。
"""

from dataclasses import dataclass, field


class Vector2D:
    """演示常用魔术方法：让向量像内置类型一样参与运算。"""

    def __init__(self, x: float, y: float):
        self.x = x
        self.y = y

    def __repr__(self) -> str:
        # repr 面向开发者：看到输出就知道怎么重建这个对象
        return f"Vector2D({self.x}, {self.y})"

    def __eq__(self, other: object) -> bool:
        # 不写 __eq__ 时 == 比较内存地址，内容相同也返回 False
        if not isinstance(other, Vector2D):
            return NotImplemented      # 和其他类型比较时交给对方处理
        return self.x == other.x and self.y == other.y

    def __add__(self, other: "Vector2D") -> "Vector2D":
        return Vector2D(self.x + other.x, self.y + other.y)

    def __abs__(self) -> float:
        # abs(v) 触发，返回向量长度
        return (self.x ** 2 + self.y ** 2) ** 0.5


v1 = Vector2D(3, 4)
v2 = Vector2D(1, 2)
print(v1 + v2)          # Vector2D(4, 6) —— + 触发 __add__，print 触发 __repr__
print(v1 == Vector2D(3, 4))   # True
print(abs(v1))          # 5.0 —— 3-4-5 直角三角形


# ============ 演示：__len__ / __getitem__ / __contains__ ============
class Playlist:
    """演示「容器类」魔术方法：让对象支持 len()、下标、for、in。"""

    def __init__(self, name: str):
        self.name = name
        self.songs: list[str] = []

    def add(self, song: str) -> None:
        self.songs.append(song)

    def __len__(self) -> int:
        return len(self.songs)

    def __getitem__(self, index: int) -> str:
        # 有了 __getitem__，对象就能被 for 遍历、切片、按下标取
        return self.songs[index]

    def __contains__(self, song: str) -> bool:
        return song in self.songs


my_list = Playlist("学习歌单")
my_list.add("晴天")
my_list.add("海阔天空")

print(len(my_list))          # 2 —— 触发 __len__
print(my_list[0])            # 晴天 —— 触发 __getitem__
for song in my_list:         # for 的遍历能力也来自 __getitem__
    print("播放：", song)
print("晴天" in my_list)     # True —— 触发 __contains__


# ============ 演示：property ============
class Temperature:
    """演示 @property：赋值时自动校验。

    _celsius 前面的下划线是约定：「这是内部变量，外部请走 celsius 属性」。
    """

    def __init__(self, celsius: float):
        # 注意：这里走的是 setter（属性已定义），所以构造时同样会被校验
        self.celsius = celsius

    @property
    def celsius(self) -> float:
        return self._celsius

    @celsius.setter
    def celsius(self, value: float) -> None:
        if value < -273.15:
            raise ValueError(f"不能低于绝对零度，收到：{value}")
        self._celsius = value

    @property
    def fahrenheit(self) -> float:
        """只读属性：换算华氏温度，不需要实例里真的存一份。"""
        return self._celsius * 9 / 5 + 32


t = Temperature(25)
print(t.fahrenheit)          # 77.0 —— 用起来像属性，背后是方法
t.celsius = 30               # 赋值触发 setter
print(t.celsius)             # 30

try:
    t.celsius = -300         # 触发 setter 校验，抛异常（呼应 01.7）
except ValueError as error:
    print("校验失败：", error)


# ============ 演示：dataclass ============
@dataclass
class Book:
    title: str
    price: float
    tags: list[str] = field(default_factory=list)  # 可变默认值的正确写法

    def discounted_price(self, rate: float = 0.8) -> float:
        return round(self.price * rate, 2)


book = Book("Python进阶", 59.9)         # 自动生成的 __repr__
print(book == Book("Python进阶", 59.9))       # False！tags 一个有值一个是空列表
print(book.discounted_price())               # 47.92

print('================  以下是02-魔术方法与dataclass的打印信息 ==================')

# ============ 练习 1：Money 运算 ============
# TODO 1：写一个 Money 类：
#   a. __init__(self, yuan)（整数元）。
#   b. __add__：Money(8) + Money(2) 返回 Money(10)（注意返回新 Money，不改自己）。
#   c. __eq__ 和 __lt__：金额相等 / 比大小；有了 __lt__ 就能 sorted。
#   d. __repr__：输出 Money(10)。

class Money:
    def __init__(self, yuan: int) -> None:
        self.yuan = yuan

    def __add__(self, other:Money):
        return Money(self.yuan + other.yuan)

    def __eq__(self, other) -> bool:
        return self.yuan == other.yuan

    def __lt__(self, other) -> bool:
            return self.yuan < other.yuan
    def __repr__(self):
        return f"Money(${self.yuan})"

print("练习 1：Money 运算 答案验证")
# 完成后取消注释验证：
prices = [Money(30), Money(15), Money(42)]
print(sorted(prices))                     # 期望 [Money(15), Money(30), Money(42)]
print(Money(8) + Money(2))                # 期望  Money(10)
print(Money(8) + Money(2) == Money(10))   # 期望 True


# ============ 练习 2：容器类 ============
# TODO 2：写一个 TodoList 类：
#   a. add(task) 添加任务。
#   b. __len__ 返回任务数。
#   c. __getitem__ 支持下标取任务（这样 for 也能遍历它）。
#   d. __contains__ 支持 "xx" in todo_list。

class TodoList:
    def __init__(self) -> None:
        self.todo_list: list[str] = []
        pass 

    def add(self, task):
        self.todo_list.append(task)
    def __len__(self):
        return len(self.todo_list)
    def __getitem__(self, index: int):
        return self.todo_list[index]
    def __contains__(self, task: str):
        return task in self.todo_list

print("练习 2：容器类 答案验证")
# 完成后取消注释验证：
todos = TodoList()
todos.add("学完面向对象")
todos.add("写作业")
print(len(todos))                  # 期望 2
print(todos[0])                    # 期望 学完面向对象
print("写作业" in todos)           # 期望 True


# ============ 练习 3：property 校验 ============
# TODO 3：写一个 StudentScore 类：
#   a. @property score + setter：分数必须在 0~100 之间，否则 raise ValueError。
#   b. @property grade（只读）：>=90 返回 "A"，>=80 "B"，>=70 "C"，>=60 "D"，否则 "E"。

class StudentScore:
    def __init__(self):
        pass

    @property
    def score(self) -> float:
        return self._score

    @score.setter
    def score(self, score: float) -> None:
        if (score < 0 or score > 100):
            raise ValueError('分数只能在0~100之间')
        self._score = score


    @property
    def grade(self):
        if self._score >= 90:
            return "A"
        if self._score >= 80:
            return "B"
        if self._score >= 70:
            return "C"
        if self._score >= 60:
            return "D"
        return "E"


print("练习 3：property 校验 答案验证")
# 完成后取消注释验证：
s = StudentScore()
s.score = 85
print(s.grade)                     # 期望 B
try:
    s.score = 120                      # 期望抛 ValueError
except ValueError as error:
    print(error)
