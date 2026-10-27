"""函数参数：定义方式与传参方式

同一个函数，定义时有不同的「接收方式」，调用时也有不同的「传递方式」，
分开看这两个视角就不乱了：
  定义时：位置参数 → 默认参数 → *args → **kwargs（顺序口诀）
  调用时：按位置传 / 按名字传 / 解包展开
* 和 ** 有两副面孔：定义时见到是「收集」，调用时见到是「展开」。
"""

# ========== 1、位置参数：按顺序一一对应 ==========
def introduce(name, city):
    print(f"{name} 来自 {city}")

# 按位置传：第一个实参给 name，第二个给 city；顺序错了值就跟着错。
introduce("小明", "北京")

# ========== 2、关键字参数：指名传参，顺序无关 ==========
# 写成 形参名=值，靠名字绑定，不怕顺序乱。
introduce(city="上海", name="小红")
# 混合传参时，位置参数必须写在关键字参数前面（先报位置，再报名字）。
introduce("小刚", city="广州")

# ========== 3、默认参数：不传就用默认值，但要小心「共享」陷阱 ==========
def power(base, exponent=2):
    return base ** exponent

print(power(3))      # 9  → exponent 用默认值 2
print(power(3, 3))   # 27 → 传入的 3 覆盖默认值

# 陷阱：默认值在「函数定义时」只创建一次，不是每次调用都新建。
def add_item_bad(item, bag=[]):        # ❌ 所有调用共享同一个列表
    bag.append(item)
    return bag

def add_item_good(item, bag=None):     # ✅ 惯用写法：None 占位，调用时才新建
    if bag is None:
        bag = []
    bag.append(item)
    return bag

print(add_item_bad("苹果"), add_item_bad("苹果"))    # ['苹果', '苹果'] ← 上次的还在！
print(add_item_good("苹果"), add_item_good("苹果"))  # ['苹果'] ['苹果'] ← 每次独立

# ========== 4、*args：收集多余的位置参数，打包成元组 ==========
def average(*args):
    # args 是元组，例如 (80, 90, 100)。args 只是习惯命名，叫别的也行。
    return sum(args) / len(args) if args else 0

print("平均分：", average(80, 90, 100))

# ========== 5、**kwargs：收集多余的关键字参数，打包成字典 ==========
def people(**kwargs):
    # kwargs 是字典，例如 {'name': '波仔', 'age': 18}。kwargs 也是习惯命名。
    print(kwargs)

people(name="波仔", age=18)

# ========== 6、定义顺序：位置 → 默认 → *args → **kwargs ==========
def profile(name, age=0, *hobbies, **extra):
    print(f"姓名：{name}，年龄：{age}")
    print(f"爱好（元组）：{hobbies}")
    print(f"其他（字典）：{extra}")

profile("小明", 18, "篮球", "编程", city="北京", job="学生")
# 分流过程：小明→name，18→age，"篮球" "编程" 是多余位置→hobbies，
# city、job 带着名字→extra。

# ========== 7、调用时解包：* 和 ** 的另一副面孔 ==========
# 4、5 段是定义时「收集」；反过来，调用时写 * / ** 是「展开」。
info = ["小红", "上海"]
introduce(*info)      # 等价于 introduce("小红", "上海")：列表拆开按位置传

extra = {"name": "小刚", "city": "广州"}
introduce(**extra)    # 等价于 introduce(name="小刚", city="广州")：字典拆开按名字传

# ========== 8、进阶提示：用 * 强制后面的参数按名字传 ==========
def create_user(name, *, is_admin=False):
    # * 之后的参数只能写 is_admin=True 传入，防止调用者靠位置传错值。
    print(f"{name}，管理员：{is_admin}")

create_user("小明", is_admin=True)
# create_user("小明", True)   # ❌ TypeError：is_admin 只接受关键字传参

# ============ 练习 TODO ============
# 1. 写 describe_pet(pet_name, animal_type="狗")：
#    分别用「全位置」「全关键字」「混合」三种方式调用，输出同样的正确结果。

def describe_pet(pet_name, animal_type="狗"):
  print(f"{animal_type} ---> {pet_name}")

describe_pet("小咪", "猫")
describe_pet(pet_name="小咪", animal_type="猫")
describe_pet("小咪", animal_type="猫")


# 2. 写 pack(sender, *items, **options)：sender 是寄件人，items 是物品列表，
#    options 是备注（如 urgent=True）。调用一次并打印三部分内容，
#    其中一次调用要求用 **字典 解包的方式传 options。

def pack(sender, *items, **options): 
  print(sender)
  print(items)
  print(options)

pack('波仔', *['苹果', '橘子'], urgent=True)


# 3. 修复 bug：下面函数多次调用后历史记录会越攒越多，为什么？怎么改？
#    def record(page, history=[]):
#        history.append(page)
#        return history

def record(page, history=None):
    if history is None:
        history = []
    history.append(page)
    return history

print(record(1))
print(record(2))
