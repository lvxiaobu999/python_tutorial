"""条件判断：if / elif / else 与逻辑表达式

条件判断的作用是：根据条件是否为 True，决定执行哪一段代码。
注意：Python 用缩进表示代码块，通常使用 4 个空格，不能只靠大括号。
"""

score = 86
# if 会先判断 score >= 90 的结果；结果为 True 才执行缩进的代码。
if score >= 90:
    level = "A"
# elif 是“否则如果”。前面的条件为 False 时，才会继续判断这里。
elif score >= 60:
    level = "B"
# 所有 if/elif 都不满足时，执行 else。
else:
    level = "C"
print(f"成绩等级：{level}")

age = 20
has_ticket = True
# and 要求左右两个条件都为 True。
# 条件表达式格式：值_if_true if 条件 else 值_if_false。
print("允许入场" if age >= 18 and has_ticket else "暂不能入场")

# ============ 练习 TODO ============
# 1. 输入一个整数，判断它是正数、负数还是 0。
int_value = int(input('请输入一个数值：'))

if int_value == 0:
    print("数字为0")
elif int_value > 0:
    print("数字为正数")
else:
    print("数字为负数")

# 2. 输入成绩（0~100），输出优秀（>=90）、良好（>=75）、及格或不及格。
score = int(input('请输入成绩：'))

if score >= 90:
    print("优秀")
elif score >= 75:
    print("良好")
elif score >= 60:
    print("及格")
else:
    print("不及格")


# 3. 判断年份是否为闰年：能被 4 整除且不能被 100 整除，或能被 400 整除。

year = int(input('请输入年份：'))

if (year % 4 == 0 and year % 100 != 0) or year % 400 == 0:
    print('是闰年')
else:
    print('不是闰年')
