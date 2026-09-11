"""异常处理：try / except / else / finally 与自定义异常"""

def parse_age(value):
    try:
        age = int(value)
        if age < 0:
            raise ValueError("年龄不能为负数")
    except ValueError as error:
        print("输入无效：", error)
        return None
    else:
        return age
    finally:
        print("年龄解析结束")

print(parse_age("18"))
print(parse_age("abc"))

# ============ 练习 TODO ============
# 1. 安全地读取两个数字并处理除数为 0 的情况。
# 2. 读取列表下标，分别处理输入类型错误和下标越界。
# 3. 为余额不足定义 InsufficientBalanceError，并在转账函数中抛出。
