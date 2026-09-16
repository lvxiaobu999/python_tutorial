"""循环：for / while、range、break、continue

循环用于重复执行一段代码。学习时可以在循环体中加入 print，观察
每一轮变量的值如何变化。
"""

total = 0
# range(1, 6) 生成一个“可迭代对象”，数字从 1 开始，到 6 之前结束：
# 1、2、3、4、5。停止值 6 不会被包含，这叫“左闭右开”。
# for 会依次把这些数字赋给 number，每次执行一次缩进代码块。
for number in range(1, 6):
    # += 等价于 total = total + number。
    total += number
print("1 到 5 的和：", total)

count = 3
# while 在每次循环开始前判断条件；只要 count > 0 就继续执行。
while count > 0:
    print("倒计时", count)
    # 如果不修改 count，条件会一直为 True，可能形成无限循环。
    count -= 1

# range(1, 11) 产生 1~10；range(起点, 终点) 不包含终点。
for number in range(1, 11):
    if number % 2 == 0:
        # % 是取余运算。偶数除以 2 的余数为 0。
        # continue 只跳过本轮后面的代码，直接进入下一轮循环。
        continue
    print("奇数：", number)

# ============ 练习 TODO ============
# 1. 用 for 计算 1~100 的偶数和。
total = 0
for number in range(2, 101, 2):
    total += number
print("1 到 100 的偶数和：", total)

# 2. 打印一个乘法表（例如 1~9）。
for i in range(1, 10):
    for j in range(1, i + 1):
        print(f"{j}×{i}={i*j}", end="\t")
    print()          # 换行


# 3. 用 while 实现猜数字游戏，猜对后用 break 结束循环。
import random

random_num = random.randint(1, 100)
last_min_value = 1 # 当前可能范围的下界
last_max_value = 100 # 当前可能范围的上界

while True:
    value = int(input(f'请输入一个正整数（{last_min_value}~{last_max_value}）：'))
    if not last_min_value <= value <= last_max_value:
        print("请输入当前范围内的数字")
        continue
    if value > random_num:
        last_max_value = min(last_max_value, value - 1)
        print(f"猜大了，答案在 {last_min_value}~{last_max_value} 之间")
    elif value < random_num:
        last_min_value = max(last_min_value, value + 1)
        print(f"猜小了，答案在 {last_min_value}~{last_max_value} 之间")
    else:
        print('回答正确：' + str(random_num))
        break
