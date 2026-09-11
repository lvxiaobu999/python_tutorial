"""循环：for / while、range、break、continue"""

total = 0
for number in range(1, 6):
    total += number
print("1 到 5 的和：", total)

count = 3
while count > 0:
    print("倒计时", count)
    count -= 1

for number in range(1, 11):
    if number % 2 == 0:
        continue
    print("奇数：", number)

# ============ 练习 TODO ============
# 1. 用 for 计算 1~100 的偶数和。
# 2. 打印一个乘法表（例如 1~9）。
# 3. 用 while 实现猜数字游戏，猜对后用 break 结束循环。
