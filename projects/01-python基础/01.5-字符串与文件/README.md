# 01.5 字符串与文件

> 这一章解决两件事：「文本怎么处理」和「数据怎么持久到磁盘」。上半章字符串，下半章文件读写。

## 知识点速查

### 1. 字符串是不可变序列

`strip()`、`upper()`、`replace()` 等**全部返回新字符串**，原字符串不变，所以必须接住返回值：

```python
clean = text.strip()          # ✅ 用变量接收新字符串
text.strip()                  # ❌ 白做，text 没有任何变化
result = clean.lower().replace("AI", "人工智能")   # 链式调用可行，因为每一步都返回新串
```

### 2. 清理与大小写方法

| 方法 | 作用 | 示例结果 |
|------|------|----------|
| `strip()` / `lstrip()` / `rstrip()` | 去首尾空白（左/右） | `" hi "` → `"hi"`，**不影响中间空格** |
| `upper()` / `lower()` | 全大写 / 全小写 | `"Py"` → `"PY"` / `"py"` |
| `capitalize()` | 首字母大写，**其余强制小写** | `"world"` → `"World"`；`"iPhone"` → `"Iphone"` |
| `title()` | 每个单词首字母大写 | `"hello world"` → `"Hello World"` |
| `swapcase()` | 大小写互换 | `"PyThon"` → `"pYTHON"` |

### 3. split 拆分与 join 拼接（互为逆操作）

```python
"  a b   c ".split()      # 无参数：按任意连续空白拆，丢弃空串 → ["a", "b", "c"]
"hello_world".split("_")  # 指定分隔符 → ["hello", "world"]
"hello__world".split("_") # 连续分隔符会产生空串 → ["hello", "", "world"]

"_".join(["hello", "world"])   # → "hello_world"，注意是「分隔符」调用 join
```

- 循环里用 `+` 拼字符串每轮都创建新串，性能差；**循环拼接用 `join`**：`"".join(parts)`。

### 4. 遍历与成员判断 `in`

```python
for ch in text:          # 字符串是序列，可直接逐字符遍历
    if ch in "aeiou":    # in 判断成员是否存在，返回 True/False
        count += 1
```

- `in` 有两种身份：`if x in s` 是**判断**，`for x in s` 是**遍历**。
- 统计类任务先 `text.lower()` 统一大小写，否则大写元音会被漏掉。

### 5. 切片 `[start:stop:step]`

| 写法 | 含义 |
|------|------|
| `s[0:6]` | 取索引 0~5，**不含 stop** |
| `s[:3]` / `s[3:]` | 开头到 2 / 从 3 到结尾 |
| `s[-3:]` | 负索引从后往前数，取最后 3 个字符 |
| `s[::-1]` | step 为 -1，从头到尾倒着取 → **反转字符串的标准写法** |

- 切片越界**不报错**（`"ab"[0:10]` → `"ab"`），但索引越界报 `IndexError`（`"ab"[5]`）。

### 6. 其他常用方法

| 方法/语法 | 作用 | 备注 |
|------|------|------|
| `s.startswith(x)` / `s.endswith(x)` | 前缀/后缀判断 | 常用于按扩展名过滤文件 |
| `s.find(x)` / `s.index(x)` | 查子串位置 | 找不到时 `find` 返回 `-1`，`index` 抛异常 |
| `s.count(x)` | 统计子串出现次数 | `"aaa".count("aa")` → 1（不重叠） |
| `s.isdigit()` / `isalpha()` / `isspace()` | 内容判断 | 注意 `"3.14".isdigit()` 是 `False`（有点号） |
| `f"{name} 有 {n} 个"` | f-string 格式化 | `{}` 里可放任意表达式，如 `{len(clean)}`、`{x:.2f}` |

### 7. 文件读写两套方式

```python
from pathlib import Path

# 方式一：小文件一次性读写（整个文件是一个字符串）
path = Path("notes.txt")
content = path.read_text(encoding="utf-8")
path.write_text("第一行\n第二行\n", encoding="utf-8")

# 方式二：with + 逐行处理（大文件友好，内存占用小）
with path.open("r", encoding="utf-8") as f:
    for line in f:            # 每次循环拿到一行，行尾带 \n
        print(line.strip())   # 常配合 strip() 去掉行尾换行
```

- `read_text()` 返回**一个大字符串**，按行处理要用 `content.splitlines()` 拆成列表（自动去掉换行符）。
- `f.readlines()` 与 `splitlines()` 的区别：前者保留 `\n`，后者不保留。
- `with` 块结束自动关闭文件，**中途抛异常也会关**，所以永远优先用 with。

### 8. 文件模式与编码

| 模式 | 含义 | 文件不存在时 |
|------|------|--------------|
| `"r"` | 只读（默认） | 报 `FileNotFoundError` |
| `"w"` | 覆盖写入，**先清空原内容** | 自动创建 |
| `"a"` | 追加写入，写在文件末尾 | 自动创建 |

- `write_text()` 只有覆盖语义、没有追加参数；要**追加**得用 `with path.open("a", encoding="utf-8") as f: f.write(...)`。
- Windows 默认编码是 GBK，处理中文**必须写 `encoding="utf-8"`**，否则乱码或 `UnicodeDecodeError`。
- 相对路径相对**运行命令时所在的目录**，不是 .py 文件所在目录；想相对脚本定位用 `Path(__file__).parent`。

## 易错点

- 调用字符串方法不接收返回值 → 原字符串纹丝不动（不可变性）。
- `split()` 无参数 vs `split("_")`：前者按空白拆并去空串，后者严格按分隔符、连续分隔符产生空串。
- 回文判断要求「忽略空格」时，`strip()` 只去**首尾**，要去所有空格得用 `s.replace(" ", "")` 或 `"".join(s.split())`。
- 大小写敏感的统计（元音、词频）忘了先 `lower()`，大写被漏掉。
- `"w"` 模式一打开就清空文件，读旧拼新前先想清楚是否该用 `"a"`。
- 写完文件看不到内容更新？先确认文件生成在**哪个目录**（相对路径跟着运行目录走）。

## 学习顺序与练习

先吃透 `01-字符串操作.py` 的方法链与切片，再做元音统计、下划线转驼峰、回文判断；然后进入 `02-文件读写.py`，完成 notes.txt 三行笔记、行数统计、去空白三个 TODO。进阶练习方向：日志分析（逐行 + startswith 过滤）、CSV 简单汇总、大文件流式处理。面试回顾重点是：字符串不可变性、`join` 与 `+` 的性能差异、`with` 的作用、UTF-8 编码。
