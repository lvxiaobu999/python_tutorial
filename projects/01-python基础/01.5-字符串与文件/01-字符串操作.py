"""字符串：索引、切片、格式化与常用方法

字符串 str 是不可变序列。strip/upper/lower/replace 都会返回新字符串，
不会原地改变原来的 text。
"""

text = "  Python makes AI   easier  "
# strip() 去除首尾空白（不会删除中间的空格）。
clean = text.strip()
# upper/lower 返回全大写/全小写的新字符串。
print(clean.upper())
# replace(old, new) 将所有匹配的 old 替换为 new。
print(clean.lower().replace("AI", "人工智能"))
# [0:6] 取索引 0~5；len() 返回字符数量。
print(clean[0:6], len(clean))
# in 用于判断子字符串是否存在，结果是 True 或 False。
print(f"文本长度：{len(clean)}，是否包含 Python：{'Python' in clean}")
# 字符串转成数组
print(text.split())
# ============ 练习 TODO ============
# 1. 输入一句话，统计其中的元音字母数量。
def get_vowels_count(text):
    count = 0
    vowels = 'aeiou'
    for s in text:
        if s in vowels:
            count += 1

    return count

print(get_vowels_count('Wishing you joy, good health, and everything you\'ve been hoping for.'))

# 2. 将下划线命名（hello_world）转换为驼峰命名（helloWorld）。
def snake_to_camel(s):
    parts = s.split('_')
    cc = ''
    for index,item in enumerate(parts):
        if index > 0:
            cc = cc + item.capitalize()
        else:
            cc = cc + item
    return cc
print(snake_to_camel('hello_world'))

# 3. 判断一个字符串是否为回文（忽略大小写和空格）。
def is_palindrome(s):
    clean = s.lower().strip()

    return clean == clean[::-1]

print(is_palindrome("level"))
print(is_palindrome("hello"))