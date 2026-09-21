"""文件读写：with、UTF-8 编码和 pathlib

Path 对象表示文件路径。write_text 会写入文本，read_text 会读取文本；
encoding="utf-8" 明确指定编码，避免中文在不同系统上出现乱码。
"""
from pathlib import Path

path = Path("学习记录.txt")
# 相对路径相对于“运行命令时所在的当前目录”，不是相对于本 .py 文件。
path.write_text("第一条学习记录\n", encoding="utf-8")
# 先读出旧内容，再拼接新内容写回，因此这里相当于追加一行。
path.write_text(path.read_text(encoding="utf-8") + "第二条学习记录\n", encoding="utf-8")
print(path.read_text(encoding="utf-8"))

# ============ 练习 TODO ============
# 1. 创建 notes.txt，写入三行学习笔记后逐行读取并编号打印。
base_dir = Path(__file__).parent
note_path = base_dir / "notes.txt"

path = Path(note_path)
path.write_text(
    "Python 文件操作需要掌握 open() 函数。\n"
    "\n"
    "with open() 可以自动关闭文件。\n"
    "\n"
    "读取文件可以使用 read()、readline() 和 readlines()。\n",
    encoding="utf-8"
)

lines = path.read_text(encoding="utf-8").splitlines()

for i, line in enumerate(lines, start=1):
    print(f"{i} ====> {line}")

# 2. 统计一个文本文件的行数、字符数和非空行数。
line_count = 0 # 行数
chart_count = 0 # 字符串数
non_empty_line_count = 0 # 非空行数

with path.open('r', encoding="utf-8") as f:
    for line in f:
        line_count += 1;
        chart_count += len(line)
        if line.strip():
            non_empty_line_count += 1


print(f"行数：{line_count}")
print(f"字符串数：{chart_count}")
print(f"非空行数：{non_empty_line_count}")

# 3. 将文件中的所有行去除首尾空白后写入 clean_notes.txt。
clean_notes_path = base_dir / "clean_notes.txt"

notePath = Path(clean_notes_path)


with path.open('r', encoding="utf-8") as f:
    with notePath.open("w", encoding="utf-8") as note:
        for line in f:
            note.write(line.strip() + "\n")