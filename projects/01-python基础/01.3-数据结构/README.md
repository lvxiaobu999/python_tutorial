# 01.3 数据结构

> 这一章解决「一批数据怎么存」。四种容器：列表、元组、字典、集合。

## 知识点速查

### 1. 列表 list（可变、有序）
```python
fruits = ["apple", "banana"]
```

| 操作 | 方法/语法 | 示例 |
|------|-----------|------|
| 末尾添加 | `append(x)` | `fruits.append("pear")` |
| 指定位置插入 | `insert(i, x)` | `fruits.insert(0, "a")` |
| 批量追加 | `extend(列表)` | `fruits.extend([1, 2])` |
| 删除某个值 | `remove(x)` | `fruits.remove("apple")` |
| 按位置删除并返回 | `pop(i=-1)` | `fruits.pop()` 删最后一个 |
| 查找索引 | `index(x)` | `fruits.index("banana")` |
| 统计出现次数 | `count(x)` | `fruits.count("a")` |
| 原地排序 | `sort()` | `fruits.sort()` |
| 原地反转 | `reverse()` | `fruits.reverse()` |
| 取子序列 | 切片 `[start:stop:step]` | `fruits[1:3]`、`fruits[::-1]` 反转 |
| 长度 | `len(列表)` | `len(fruits)` |

- 访问/修改元素：`fruits[0]`、`fruits[0] = "grape"`
- 判断存在：`"apple" in fruits`

### 2. 元组 tuple（不可变、有序）
```python
point = (10, 20)
x, y = point   # 解包
```
- 和列表几乎一样，但**不能增删改**（没有 append、不能改元素）。
- 单个元素要加逗号：`(5,)` 才是元组，`(5)` 只是数字 5。

### 3. 字典 dict（键值对）
```python
user = {"name": "小明", "age": 18}
```

| 操作 | 方法/语法 |
|------|-----------|
| 取值 | `user["name"]` 或 `user.get("name")` |
| 取不到给默认值 | `user.get("email", "未填写")` |
| 添加/修改 | `user["city"] = "北京"` |
| 删除 | `user.pop("age")` 或 `del user["age"]` |
| 遍历键/值/键值对 | `.keys()` / `.values()` / `.items()` |
| 判断 key 是否存在 | `"name" in user` |

### 4. 集合 set（无序、自动去重）
```python
tags = {"python", "ai", "python"}   # 自动去重 → {"python", "ai"}
```
- 增删：`add(x)`、`remove(x)` / `discard(x)`（discard 删不存在的值不报错）
- 集合运算：`|` 并集、`&` 交集、`-` 差集、`^` 对称差
- 注意：`set()` 是空集合，`{}` 是空字典。

## 四者对比速记

| 类型 | 可变 | 有序 | 重复元素 | 用途 |
|------|------|------|----------|------|
| list | ✅ | ✅ | 允许 | 会变化的序列 |
| tuple | ❌ | ✅ | 允许 | 固定搭配（坐标、日期） |
| dict | ✅ | 按插入序 | key 不重复 | 键值映射 |
| set | ✅ | ❌ | 不允许 | 去重、集合运算 |

## 易错点
- `remove(x)` 删不存在的值会报错，`discard(x)` 不会。
- 找最大/最小值要用**两个独立的判断**，别用 if/else 绑在一起。
- `max`/`min`/`list`/`dict` 等是内置函数名，别拿它们当变量名（会覆盖内置功能）。

## 学习顺序与练习

建议先运行 `01-列表与元组.py`，观察索引和切片，再运行 `02-字典与集合.py`，观察键值查找和集合运算。完成基础 TODO 后，继续做成绩分析器、列表去重保序、两数之和和词频统计；提交时写明主要数据结构及时间复杂度。
