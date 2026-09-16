"""列表与元组：有序容器、切片和常用方法

列表 list 是有序、可修改的容器；元组 tuple 是有序、不可修改的容器。
索引从 0 开始，切片使用 [start:stop:step]，同样不包含 stop。
"""

fruits = ["apple", "banana", "orange"]
# append 在列表末尾添加一个元素，列表长度会增加。
fruits.append("pear")
# 通过索引修改元素；fruits[1] 表示第二个元素。
fruits[1] = "grape"
print("列表：", fruits)
# fruits[:2] 等价于 fruits[0:2]，取得第 0、1 个元素，不包含索引 2。
print("切片：", fruits[:2])

point = (10, 20)
# 元组拆包：把两个位置的值依次赋给 x 和 y。
x, y = point
print(f"坐标：({x}, {y})，长度：{len(point)}")

# ============ 练习 TODO ============
# 1. 创建购物清单，完成添加、删除、排序并打印总数量。
shop_list = [("苹果", 6),("香蕉", 3),("橘子", 5)]

####### 一、添加
while True:
    shop_name = input('请输入商品名称：')
    shop_count = int(input('请输入商品数量：'))
    shop_list.append((shop_name, shop_count))

    # 是否继续添加
    choice = input('是否继续添加？(y/n)：')
    if choice.lower() != 'y':
        break

print('\n当前清单：')



#######  二、删除

while True:
    # enumerate 的作用是同时拿到索引和值
    for i,(shop_name, shop_count) in enumerate(shop_list):
        print(f'{i}. {shop_name} x {shop_count}')

    idx = input('输入要删除的编号（回车跳过）：')
    if idx == '':
        break
    if idx.isdigit() and 0 <= int(idx) < len(shop_list):
        removed = shop_list.pop(int(idx))
        print(f'已删除：{removed[0]}')
    else:
        print('编号无效')

print('\n剩下清单：')
print(shop_list)

####### 三、排序
shop_list.sort(key=lambda x: x[1], reverse=True)
print('\n排序后的清单：')
print(shop_list)

# 2. 找出列表中的最大值、最小值和平均值。
# 这里使用内置函数 max/min，避免把它们覆盖成变量名。
counts = [shop_count for _, shop_count in shop_list]
if counts:
    total = sum(counts)
    max_count = max(counts)
    min_count = min(counts)
    print(f'最大值是: {max_count}')
    print(f'最小值是: {min_count}')
    print(f'平均值是: {total / len(counts):.2f}')
else:
    print('清单为空，无法统计最大值、最小值和平均值')

# 3. 将一个列表切片反转，并说明列表与元组的主要区别。

# 切片反转三种方式
reversed_shop_list = shop_list[::-1] # 返回新列表
# shop_list.reverse() # 改变原列表
# reversed_shop_list = list(reversed(shop_list)) # 返回新列表

# ============ 列表 vs 元组：核心区别 ============
# 一句话：列表可变（能增删改），元组不可变（创建后不能改）
#
# 1) 列表 list：有 append/remove，可以直接改元素
# 2) 元组 tuple：没有增删改方法，元素只读
#
# 用代码实际验证一下：

fruits_list = ["apple", "banana"]
fruits_list.append("pear")        # ✅ 列表可以添加元素
fruits_list[0] = "grape"          # ✅ 列表可以修改元素
print("列表可变：", fruits_list)   # ['grape', 'banana', 'pear']

point_tuple = (10, 20)
# point_tuple[0] = 99             # ❌ 报错：'tuple' object does not support item assignment
# point_tuple.append(30)          # ❌ 报错：元组没有 append 方法
print("元组不可变：", point_tuple) # (10, 20)

# 其它区别（进阶了解）：
# - 元组不可变、可哈希，所以能当字典的 key；列表不能
# - 元组更省内存、通常更快
# - 语义上：元组常表示「固定搭配」（坐标、日期），列表表示「会变化的集合」（购物清单、待办）
