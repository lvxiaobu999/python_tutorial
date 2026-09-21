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

# ============ 练习 TODO ============
# 1. 安全地读取两个数字并处理除数为 0 的情况。
def divide():
    try:
        a = int(input('请输入被除数的值：'))
        b = int(input('请除数的值：'))
       
        if b == 0:
            raise ValueError('除数不能为0')
    except TypeError as error:
        print("TypeError", error)
        return None
    except ValueError as error:
        print('ValueError', error)
        return None
    else:
        return a / b
    finally:   
        print(f"不管失败还是成功都要执行finally")
result = divide()
print(f"商是{result}")
# 2. 读取列表下标，分别处理输入类型错误和下标越界。
def read_index(index):
    fruits = ["苹果", "香蕉", "橙子"]
    try:
        if type(index) != int:
            raise TypeError('请输入一个有效的数字')
        if index < 0:
            raise ValueError('请输入一个大于0的数字')
        if index >= len(fruits):
            raise IndexError(f"最大索引只能是：{len(fruits)}")
    except TypeError as error:
            print("TypeError", error)
            return None
    except IndexError as error:
        print('IndexError', error)
        return None
    except Exception as error:
        print(error)
    else:
        return fruits[index]
    finally:   
        print(f"不管失败还是成功都要执行finally")

print(read_index('fsdf'))  
print(read_index(5)) 
print(read_index(1))  

# 3. 为余额不足定义 InsufficientBalanceError，并在转账函数中抛出。
class InsufficientBalanceError(Exception):
    def __init__(self, balance) -> None:
        super().__init__(f"余额不足：现有余额 {balance}元")
        self.balance = balance

def transfer(amount):
    balance = 100
    try:
        if amount > balance:
            raise InsufficientBalanceError(balance)
    except InsufficientBalanceError as error:
        print(error)
    else:
        print(f"已转账成功：{amount}元")

transfer(101)
transfer(100)