"""列表与元组：有序容器、切片和常用方法"""

fruits = ["apple", "banana", "orange"]
fruits.append("pear")
fruits[1] = "grape"
print("列表：", fruits)
print("切片：", fruits[:2])

point = (10, 20)
x, y = point
print(f"坐标：({x}, {y})，长度：{len(point)}")

# ============ 练习 TODO ============
# 1. 创建购物清单，完成添加、删除、排序并打印总数量。
# 2. 找出列表中的最大值、最小值和平均值。
# 3. 将一个列表切片反转，并说明列表与元组的主要区别。
