"""01.1 语法基础 · 类型转换

int() / float() / str() / bool()

运行：uv run python "01.1-语法基础/03-类型转换.py"
"""

# ============ 1. 各类型之间的转换 ============
print(int("123"))        # 123（字符串 -> 整数）
print(int(3.99))         # 3（浮点 -> 整数，直接截断，不四舍五入）
print(float("3.14"))     # 3.14
print(float(10))         # 10.0
print(str(123))          # "123"（整数 -> 字符串）
print(str(3.14))         # "3.14"

# bool()：什么会转成 False？
print(bool(0))           # False
print(bool(""))          # False（空字符串）
print(bool(1))           # True
print(bool("abc"))       # True（非空字符串）

# ============ 2. input() 读取输入 ============
# input() 永远返回字符串，需要类型转换。
# 想试交互版就把下面两行取消注释：
# name = input("你叫什么名字？")
# age = int(input("你多大了？"))
# print(f"{name} 明年 {age + 1} 岁")

# 无需交互的演示：模拟 input() 的返回值
raw = input('请输入年龄：')              # 假设这是 input() 的返回值
age = int(raw)
print("明年", age + 1)  # 26

# ============ 3. 常见的坑：拼接数字需要先转字符串 ============
n = 5
# print("我有 " + n + " 个苹果")        # 报错：不能 str + int
print("我有 " + str(n) + " 个苹果")     # 正确：先转 str

# ============ 练习 TODO ============
# 1. 写一个程序：输入半径，计算圆的面积（π 用 3.14，面积 = π * r * r）
#   提示：radius = float(input("输入半径："))

r = float(input('请输入圆形的半径(单位是：米)：'))

area = 3.14 * r * r

print("圆形的面积为{}平方米".format(area))
