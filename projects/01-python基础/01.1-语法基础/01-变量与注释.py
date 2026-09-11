"""01.1 语法基础 · 变量与注释

学习目标：
    1. 用 = 给变量赋值
    2. 变量命名规则
    3. 用 type() 查看类型
    4. 写注释（# 单行、三引号多行）

运行：uv run python "01.1-语法基础/01-变量与注释.py"
"""

# ============ 1. 变量赋值 ============
# 语法：变量名 = 值
name: str = "小明"           # 字符串 str
age = 20                # 整数 int
height = 1.75           # 小数（浮点数）float
is_student = True       # 布尔 bool

print(name, age, height, is_student)

# ============ 2. type() 查看类型 ============
print(type(name))        # <class 'str'>
print(type(age))         # <class 'int'>
print(type(height))      # <class 'float'>
print(type(is_student))  # <class 'bool'>

# ============ 3. 变量可以重新赋值（动态类型）============
x = 10
print(x, type(x))        # 10 <class 'int'>
x = "现在是字符串了"
print(x, type(x))        # 现在是字符串了 <class 'str'>

# ============ 4. 命名规则 ============
# 合法：字母/下划线开头，后跟字母/数字/下划线
user_name = "ok"
_name = "也ok"
age2 = "ok"
# 2age = "不ok，不能数字开头"      # 取消注释会报错
# user-name = "不ok，不能用连字符" # 会报错

# 约定：变量名用 snake_case（小写 + 下划线），见上面的 user_name

# ============ 练习 TODO ============
# 1. 创建三个变量，分别存你的名字、年龄、城市，并打印
# 2. 用 type() 打印它们的类型

my_name = 'bozai'
my_age = 25
my_city = 'shanghai'

print(f"{type(my_name)} ----> {my_name}")
print(f"{type(my_age)} ----> {my_age}")
print(f"{type(my_city)} ----> {my_city}")
