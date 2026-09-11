"""模块与包：import、标准库和入口保护"""
import math
import random
from datetime import date

print("圆面积：", math.pi * 3 ** 2)
print("随机数：", random.randint(1, 10))
print("今天：", date.today())

if __name__ == "__main__":
    print("直接运行当前文件")

# ============ 练习 TODO ============
# 1. 使用 pathlib 和 datetime 生成带日期的学习日志文件名。
# 2. 把计算器函数放入 calculator.py，再在本文件导入并调用。
# 3. 查阅 random 模块，实现随机抽取不重复的 3 个数字。
