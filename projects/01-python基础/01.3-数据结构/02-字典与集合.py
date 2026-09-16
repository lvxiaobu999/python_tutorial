"""字典与集合：键值映射、去重和集合运算

字典 dict 用“键 -> 值”保存映射；集合 set 只保存不重复的元素，
并支持交集、并集、差集等集合运算。
"""

user = {"name": "小明", "age": 18}
# 用字典[key] 写入新键或修改已有键。
user["city"] = "北京"
# get(key, 默认值) 在键不存在时不会抛 KeyError。
print(user.get("name"), user.get("email", "未填写邮箱"))
# items() 同时返回每一项的键和值，可用于遍历字典。
for key, value in user.items():
    print(key, "=", value)

tags = {"python", "ai", "python"}
# 集合会自动去重，因此 python 只保留一次；集合输出顺序不保证固定。
print("去重后的标签：", tags)
# & 是交集运算：只保留同时出现在两个集合中的元素。
print("共同标签：", tags & {"ai", "web"})

# ============ 练习 TODO ============
# 1. 统计一句话中每个字符出现的次数（使用字典）。
s = "hello world"
count_dict = {}
for item in s:
    count_dict[item] = count_dict.get(item, 0) + 1

print(count_dict)

# 2. 合并两份商品库存字典，同名商品数量相加。
dict1 = {'苹果': 5, '香蕉': 3, '橙子': 2}
dict2 = {'香蕉': 4, '橙子': 6, '葡萄': 7}

# 第一步：先把 dict1 全部放进去
dict3 = dict1.copy()
# 第二步：遍历 dict2，逐个累加
for key, value in dict2.items():
    if key in dict3:
        dict3[key] = dict3[key] + value   # 用旧值累加 ✅
    else:
        dict3[key] = value                # 新商品直接放
print(dict3)
# {'苹果': 5, '香蕉': 7, '橙子': 8, '葡萄': 7}

from collections import Counter
dict4 = Counter(dict1) + Counter(dict2)
print(dict4)
print(dict(dict4))

# 3. 使用集合找出两门课程共同的学生和各自独有的学生。
python_students = {"小明", "小红", "小刚", "小丽"}
web_students = {"小红", "小丽", "小强"}
print("共同学生：", python_students & web_students)
print("只学 Python：", python_students - web_students)
print("只学 Web：", web_students - python_students)
# print(python_students | web_students)
