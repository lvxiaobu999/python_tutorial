"""01.1 语法基础 · 数据类型（数字 / 字符串 / 布尔）

运行：uv run python "01.1-语法基础/02-数据类型.py"
"""

# ============ 1. 数字 ============
# int 表示整数，float 表示带小数的浮点数。/ 的结果总是浮点数。
# // 是整除（向下取整），% 是取余，** 是幂运算。
a = 10          # 整数 int
b = 3
print("加法", a + b)
print("减法", a - b)
print("乘法", a * b)
print("除法（结果是浮点数）", a / b)
print("整除", a // b)      # 3
print("取余", a % b)       # 1
print("幂", a ** b)        # 1000

pi = 3.14       # 浮点数 float
print("浮点数", pi, type(pi))

# ============ 2. 字符串 ============
# 单引号和双引号都能创建字符串；三引号可以保存跨行文本。
s1 = '单引号'
s2 = "双引号"
s3 = '''三引号
可以跨行'''
print(s1, s2, s3)

# + 拼接字符串，* 重复字符串；两边类型不一致时不能直接用 +。
greeting = "Hello" + " " + "World"
repeat = "哈" * 3
print(greeting)   # Hello World
print(repeat)     # 哈哈哈

# len() 求长度
print("长度", len("Python"))   # 6

# ============ 3. 布尔与比较 ============
# 比较表达式会产生 True/False。== 判断相等，= 是赋值，不能混用。
t = True
f = False
print(10 > 3)     # True
print(10 == 3)    # False
print(10 != 3)    # True
print(1 <= 2)     # True

# 逻辑运算 and / or / not
print(True and False)   # False
print(True or False)    # True
print(not True)         # False

# ============ 练习 TODO ============
# 1. 计算 100 秒是多少分钟多少秒
# 2. 用字符串拼接打印一句话介绍你自己

seconds = 100

m = seconds // 60
s = seconds % 60

print(f"100秒是{str(m)}分{str(s)}秒")

name = 'bozai'
age = 25

print("你好！我是" + name + "，今年" + str(age) + "岁。")
