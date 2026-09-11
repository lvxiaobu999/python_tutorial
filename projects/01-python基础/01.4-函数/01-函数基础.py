"""函数：定义、参数、返回值、默认参数和可变参数"""

def greet(name, prefix="你好"):
    return f"{prefix}，{name}！"

def average(*numbers):
    return sum(numbers) / len(numbers) if numbers else 0

print(greet("小明"))
print("平均分：", average(80, 90, 100))

# ============ 练习 TODO ============
# 1. 编写 rectangle_area(width, height)，返回矩形面积。
# 2. 编写 is_prime(number)，判断一个数是否为质数。
# 3. 编写 word_count(text)，返回文本中单词及其次数组成的字典。
