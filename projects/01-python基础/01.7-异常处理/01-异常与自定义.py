"""异常处理：try / except / else / finally 与自定义异常

异常表示运行过程中出现了无法正常处理的情况。try 放可能出错的代码，
except 处理指定异常，else 在没有异常时执行，finally 无论是否出错都会执行。
"""

def parse_age(value):
    try:
        # int("abc") 会抛 ValueError；下面主动 raise 也会进入 except。
        age = int(value)
        if age < 0:
            raise ValueError("年龄不能为负数")
    except ValueError as error:
        # as error 把异常对象保存下来，可读取其中的错误消息。
        print("输入无效：", error)
        return None
    else:
        # 只有 try 中没有异常时才会执行这里。
        return age
    finally:
        # 清理资源、打印日志等收尾动作适合放在 finally。
        print("年龄解析结束")

print(parse_age("18"))
print(parse_age("abc"))


# ============ 练习 1：安全除法 ============
def divide():
    try:
        a = int(input('请输入被除数的值：'))
        b = int(input('请输入除数的值：'))
        # 除法放在 try 里：除数为 0 时 Python 自己抛 ZeroDivisionError，
        # 不需要 if b == 0 手动判断（EAFP 风格：先做，错了再捕）。
        result = a / b
    except ValueError as error:
        print("ValueError", error)
        return None
    except ZeroDivisionError as error:
        print("ZeroDivisionError", error)
        return None
    else:
        # 注意：else 不受上面 except 保护，所以出错的动作必须放在 try 里。
        return result
    finally:
        print("不管失败还是成功都要执行finally")


result = divide()
if result is not None:
    print(f"商是{result}")


# ============ 练习 2：安全取列表元素 ============
def read_index(index):
    fruits = ["苹果", "香蕉", "橙子"]
    try:
        # 直接取元素：字符串下标 Python 抛 TypeError；
        # 越界（正反两个方向都算）抛 IndexError，负数漏不掉。
        fruit = fruits[index]
    except TypeError as error:
        print("TypeError", error)
        return None
    except IndexError as error:
        print("IndexError", error)
        return None
    else:
        return fruit
    finally:
        print("不管失败还是成功都要执行finally")


print(read_index('fsdf'))    # TypeError：字符串不是合法下标
print(read_index(5))         # IndexError：越界
print(read_index(-10))       # IndexError：负数越界同样能捕获
print(read_index(1))         # 正常返回香蕉
print(read_index(-1))        # -1 是合法的负索引，返回橙子


# ============ 练习 3：自定义异常与转账 ============
class InsufficientBalanceError(Exception):
    """余额不足时抛出，携带余额和转账额，处理方可以直接读取。"""

    def __init__(self, balance, amount) -> None:
        super().__init__(f"余额不足：现有余额 {balance}元，本次需转账 {amount}元")
        self.balance = balance
        self.amount = amount


def transfer(balance, amount):
    """只负责校验和抛出，成功返回新余额；失败怎么处理由调用方决定。"""
    if amount > balance:
        raise InsufficientBalanceError(balance, amount)
    return balance - amount


# 调用方捕获：自定义异常的价值就是能精确捕获业务错误，还能读取携带的字段。
try:
    print("转账成功，剩余：", transfer(100, 30), "元")
    print("转账成功，剩余：", transfer(100, 100), "元")
    print("转账成功，剩余：", transfer(100, 101), "元")
except InsufficientBalanceError as error:
    print("转账失败：", error)
    print("还差：", error.amount - error.balance, "元")
