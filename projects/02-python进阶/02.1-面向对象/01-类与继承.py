"""面向对象（一）：类与实例、三种方法、继承与多态

类是图纸，实例是照图纸造出的对象；继承复用父类的属性和方法；
多态 = 同一个调用，不同子类各自执行自己的版本。
"""


class BankAccount:
    """演示：类属性、实例属性、实例方法。"""

    bank_name = "Python银行"          # 类属性：所有实例共享一份
    account_count = 0                 # 用来统计「一共开了几个账户」

    def __init__(self, owner: str, balance: float):
        # __init__ 在 BankAccount(...) 创建实例时自动调用
        self.owner = owner            # 实例属性：每个账户各自的
        self.balance = balance
        BankAccount.account_count += 1  # 注意：改类属性要写「类名.属性」

    def deposit(self, amount: float) -> None:
        self.balance += amount

    def withdraw(self, amount: float) -> None:
        if amount > self.balance:
            raise ValueError(f"余额不足：现有 {self.balance}，要取 {amount}")
        self.balance -= amount

    @classmethod
    def from_promo(cls, owner: str) -> "BankAccount":
        """类方法当「替代构造器」：新客户开户送 50 元。

        cls 就是类本身（可能是子类），所以用 cls(...) 而不是写死 BankAccount(...)。
        """
        return cls(owner, 50)

    @staticmethod
    def is_valid_amount(amount: float) -> bool:
        """静态方法：不需要读实例数据，只是和「金额」相关的纯函数。"""
        return amount > 0


account = BankAccount("小明", 100)
account.deposit(50)
print(account.owner, account.balance)              # 小明 150
print(BankAccount.account_count)                   # 1

promo = BankAccount.from_promo("小红")             # 走类方法开户
print(promo.owner, promo.balance)                  # 小红 50
print(BankAccount.account_count)                   # 2
print(BankAccount.is_valid_amount(-1))             # False


# ============ 演示：继承与多态 ============
class Animal:
    def __init__(self, name: str):
        self.name = name

    def speak(self) -> str:
        return f"{self.name}发出了声音"


class Dog(Animal):
    def __init__(self, name: str, breed: str):
        super().__init__(name)      # 委托父类完成 name 的初始化
        self.breed = breed

    def speak(self) -> str:         # 重写父类方法
        return f"{self.name}（{self.breed}）：汪！"


class Cat(Animal):
    def speak(self) -> str:
        return f"{self.name}：喵～"


class Robot:                        # 注意：和 Animal 没有继承关系！
    def speak(self) -> str:
        return "机器人：哔哔"


# 多态 + 鸭子类型：只要求「有 speak 方法」，根本不检查继承自谁。
for speaker in [Dog("旺财", "柴犬"), Cat("咪咪"), Robot()]:
    print(speaker.speak())

print(isinstance(Dog("旺财", "柴犬"), Animal))   # True：子类实例也是父类实例

print('================  以下是01-类与继承作业的打印信息 ==================')


# ============ 练习 1：Student 类 ============
class Student:
    """TODO 1：按下述要求完成这个类。

    要求：
    a. __init__(self, name, scores)：scores 是各科分数的列表，存到实例属性。
    b. 类属性 created_count：每创建一个 Student 实例就 +1（提示：在 __init__ 里改类名.属性）。
    c. average() 方法：返回平均分（sum/len）。
    d. __repr__：输出 Student(name='xx', 平均分=xx)。
    """

    created_count = 0

    def __init__(self, name, scores):
        self.name = name
        self.scores = scores

        Student.created_count += 1

    def average(self):
        if (len(self.scores) == 0):
            return 0
        total = 0
        for score in self.scores:
            total += score
        
        return total / len(self.scores)

    def __repr__(self):
        return f"Student(name='{self.name}', 平均分={self.average()})"

print('练习一答案验证======================')
# 完成后取消注释验证：
s1 = Student("小明", [85, 92, 78])
s2 = Student("小红", [90, 88, 95])
print(s1.average())                  # 期望 85.0
print(s1)                            # 期望 Student(name='小明', 平均分=85.0)
print(Student.created_count)         # 期望 2


# ============ 练习 2：继承与多态 ============
# TODO 2：定义 Shape 基类和两个子类：
#   a. Shape 有 __init__(self, name)，方法 area() 返回 0。
#   b. Circle(Shape)：__init__ 接收 radius，area() 返回 3.14159 * radius ** 2。
#   c. Rectangle(Shape)：__init__ 接收 width/height，area() 返回 width * height。
#   d. 把三种图形放进同一个列表，循环打印「名字：面积」，体会多态。

class Shape:
    def __init__(self, name) -> None:
        self.name = name

    def area(self):
        return 0

class Circle(Shape):
    def __init__(self, radius) -> None:
        super().__init__('圆')
        self.radius = radius

    def area(self):
        return 3.14159 * self.radius ** 2
class Rectangle(Shape):
    def __init__(self, width, height) -> None:
        super().__init__('矩形')
        self.width = width
        self.height = height

    def area(self):
        return self.height * self.width

print('练习二答案验证======================')
# 完成后取消注释验证：
for shape in [Circle(2), Rectangle(3, 4), Shape("未知")]:
    print(f"{shape.name}：{shape.area():.2f}")
# 期望输出：
# 圆：12.57
# 矩形：12.00
# 未知：0.00


# ============ 练习 3：类方法替代构造器 ============
# TODO 3：仿照 BankAccount.from_promo，写一个 Employee 类：
#   a. __init__(self, name, salary)。
#   b. 类方法 from_string(cls, text)：解析 "张三,8000" 这样的字符串创建实例。
#      提示：text.split(",") 拆开，salary 要 int() 转换。

class Employee:
    def __init__(self, name: str, salary: int) -> None:
        self.name = name
        self.salary = salary

    @classmethod
    def from_string(cls, text: str) -> Employee:
        arr = text.split(",")
        name = arr[0]
        salary = arr[1]
        return cls(name, int(salary))

print('练习三答案验证======================')
# 完成后取消注释验证：
e = Employee.from_string("张三,8000")
print(e.name, e.salary)             # 期望：张三 8000
