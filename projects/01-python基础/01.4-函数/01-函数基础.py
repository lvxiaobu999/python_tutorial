"""函数：定义、参数、返回值、默认参数和可变参数

函数是可重复调用的代码块。def 定义函数，return 把结果交还给调用者；
没有 return 时函数默认返回 None。
"""

def greet(name, prefix="你好"):
    # name 是必填参数，prefix 是有默认值的参数。
    # 调用 greet("小明") 时，prefix 自动使用“你好”。
    return f"{prefix}，{name}！"

def average(*numbers):
    # *numbers 会把任意数量的位置参数收集成一个元组。
    # 空元组时不能直接除以 len，因此先返回 0。
    return sum(numbers) / len(numbers) if numbers else 0

print(greet("小明"))
print("平均分：", average(80, 90, 100))

# ============ 练习 TODO ============
# 1. 编写 rectangle_area(width, height)，返回矩形面积。
def rectangle_area(width: int, height: int):
    return width  * height

print(rectangle_area(10, 20))

# 2. 编写 is_prime(number)，判断一个数是否为质数。
def is_prime(number: int):
    if number <= 1:
        return False

    if number == 2:
        return True

    if number % 2 == 0: # 偶数除了2都不是质数
        return False

    for i in range(3, int(number ** 0.5) + 1, 2):
        if number % i == 0:
            return False
    return True    

while True:
    number = input('请输入一个整数（输入 q 退出）:')

    if number.lower() == 'q':
        print("已退出")
        break

    isTrue = is_prime(int(number))
    print(f"{number}{'是质数' if isTrue else '不是质数'}")

# 3. 编写 word_count(text)，返回文本中单词及其次数组成的字典。
def word_count(text: str):
    result = {}
    for word in text.split():
        result[word] = result.get(word,0) + 1
    return result

text = "Wishing you all the happiness and success in the world."

print(word_count(text))