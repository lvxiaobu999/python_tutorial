"""字符串：索引、切片、格式化与常用方法"""

text = "  Python makes AI easier  "
clean = text.strip()
print(clean.upper())
print(clean.lower().replace("AI", "人工智能"))
print(clean[0:6], len(clean))
print(f"文本长度：{len(clean)}，是否包含 Python：{'Python' in clean}")

# ============ 练习 TODO ============
# 1. 输入一句话，统计其中的元音字母数量。
# 2. 将下划线命名（hello_world）转换为驼峰命名（helloWorld）。
# 3. 判断一个字符串是否为回文（忽略大小写和空格）。
