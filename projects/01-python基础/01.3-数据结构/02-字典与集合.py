"""字典与集合：键值映射、去重和集合运算"""

user = {"name": "小明", "age": 18}
user["city"] = "北京"
print(user.get("name"), user.get("email", "未填写邮箱"))
for key, value in user.items():
    print(key, "=", value)

tags = {"python", "ai", "python"}
print("去重后的标签：", tags)
print("共同标签：", tags & {"ai", "web"})

# ============ 练习 TODO ============
# 1. 统计一句话中每个字符出现的次数（使用字典）。
# 2. 合并两份商品库存字典，同名商品数量相加。
# 3. 使用集合找出两门课程共同的学生和各自独有的学生。
