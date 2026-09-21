"""模块与包：import、标准库和入口保护

模块就是一个 .py 文件。导入模块后，可以使用“模块名.成员名”调用其中
的函数、类或常量，从而复用代码而不必重复编写。
"""
import math
import random
from datetime import date
from calculator import multiply
from pathlib import Path

# math.pi 是 math 模块提供的圆周率常量；** 是幂运算。
print("圆面积：", math.pi * 3 ** 2)
# randint(a, b) 会返回包含 a 和 b 的随机整数。
print("随机数：", random.randint(1, 10))
# from ... import ... 只导入指定成员，可以直接写 date.today()。
print("今天：", date.today())

# 直接运行本文件时 __name__ 等于 "__main__"；被别的文件导入时不等于它。
# 入口保护可以避免导入模块时意外执行命令行程序代码。
if __name__ == "__main__":
    print("直接运行当前文件")

# ============ 练习 TODO ============
# 1. 使用 pathlib 和 datetime 生成带日期的学习日志文件名。

path_dir = Path(__file__).parent

log_file = path_dir / f"{date.today()}-01-模块导入.log"


log_file.write_text(
    "学习先运行示例，比较 `import` 和 `from ... import ...` 的调用方式，再把计算器拆成独立模块。\n"
    "完成基础 TODO 后，继续拆分一个可复用 CLI 包，并用 `argparse` 增加命令行参数；\n"
    "面试回顾重点是模块搜索路径、包初始化和循环导入。",
    encoding="utf-8"
)


# 2. 把计算器函数放入 calculator.py，再在本文件导入并调用。
result = multiply(6, 6)
print(result)
# 3. 查阅 random 模块，实现随机抽取不重复的 3 个数字。
numbers = random.sample(range(1, 11), 3)

print(numbers)