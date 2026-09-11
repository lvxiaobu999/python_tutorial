"""条件判断：if / elif / else 与逻辑表达式"""

score = 86
if score >= 90:
    level = "A"
elif score >= 60:
    level = "B"
else:
    level = "C"
print(f"成绩等级：{level}")

age = 20
has_ticket = True
print("允许入场" if age >= 18 and has_ticket else "暂不能入场")

# ============ 练习 TODO ============
# 1. 输入一个整数，判断它是正数、负数还是 0。
# 2. 输入成绩（0~100），输出优秀（>=90）、良好（>=75）、及格或不及格。
# 3. 判断年份是否为闰年：能被 4 整除且不能被 100 整除，或能被 400 整除。
