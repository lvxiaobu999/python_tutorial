"""文件读写：with、UTF-8 编码和 pathlib"""
from pathlib import Path

path = Path("学习记录.txt")
path.write_text("第一条学习记录\n", encoding="utf-8")
path.write_text(path.read_text(encoding="utf-8") + "第二条学习记录\n", encoding="utf-8")
print(path.read_text(encoding="utf-8"))

# ============ 练习 TODO ============
# 1. 创建 notes.txt，写入三行学习笔记后逐行读取并编号打印。
# 2. 统计一个文本文件的行数、字符数和非空行数。
# 3. 将文件中的所有行去除首尾空白后写入 clean_notes.txt。
