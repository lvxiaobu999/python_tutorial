"""04.6 测试套件：pytest + TestClient——02.7 的正式兑现

02.7 练的断言 / fixture / parametrize 在这里全部上岗：不经过网络，
把请求直接打进 06-测试与部署.py 里的 app，逐个接口断言响应码与响应体。

运行（在 projects/04-fastapi进阶 目录下，注意不是 fastapi dev）：
    uv run pytest "04.6-测试与部署/test_06.py" -v
    # 等价：./.venv/Scripts/python.exe -m pytest "04.6-测试与部署/test_06.py" -v

观察什么：
1. -v 输出里每个 test_ 函数占一行 PASSED——测试名本身就是一行行为说明；
2. 故意改坏一个断言（比如把 201 改成 200）再跑，pytest 会打印 assert 的
   左右两边——定位失败不靠猜；
3. 全套 10 条测试不到一秒：这就是 TestClient 不起服务器的好处。
"""

import importlib.util
from pathlib import Path

import pytest
from fastapi.testclient import TestClient

# ============ 0、加载被测模块：文件名 import 不了，只能按路径手动加载 ============
# 「06-测试与部署」以数字开头、带连字符，不是合法的 Python 标识符，
# 写不出普通的 import 语句；用 importlib 按文件路径加载——顺便看穿
# import 的本质：找到文件 → 执行一遍 → 拿到它创建的命名空间。
_APP_PATH = Path(__file__).with_name("06-测试与部署.py")
_spec = importlib.util.spec_from_file_location("books_app", _APP_PATH)
books_app = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(books_app)

# 一本「标准样本书」：多个测试共用，谁动了字段一眼就能看出来
BOOK = {"title": "三体", "author": "刘慈欣", "price": 45.0, "rating": 4.5}


# ============ 1、fixture：每个测试领一台「进程内客户端」+ 一份干净数据 ============
@pytest.fixture()
def client():
    """02.7 的 fixture 在这里兑现：测试函数只要声明 client 参数，
    pytest 就把准备好的 TestClient 递进来——准备与验证彻底分离。

    两个关键动作：
    1. reset_books()：books 是模块级 dict，比任何测试都活得久，上一个测试
       插的书会残留给下一个——必须显式清空，否则测试就有了顺序依赖（易错点）；
    2. with TestClient(...)：用完自动关闭。现在 app 没有 lifespan 也无妨，
       等到 04.1 里 app 要在启动时建表，这个写法就不用改。
    """
    books_app.reset_books()
    with TestClient(books_app.app) as c:
        yield c


# ============ 2、状态隔离的哨兵：每个测试都从「空书架」开始 ============
def test_books_start_empty(client):
    """GET 列表（03.2 路由）应为空——如果 fixture 忘了 reset_books()，
    这条会先红：让测试自己守护「测试之间互不污染」的前提。"""
    resp = client.get("/books")
    assert resp.status_code == 200
    assert resp.json() == {"books": []}


# ============ 3、POST 创建 → 201（03.1 POST 路由 + 03.4 状态码） ============
def test_create_book_returns_201(client):
    resp = client.post("/books", json=BOOK)
    assert resp.status_code == 201  # 03.4：status_code=201 的兑现
    body = resp.json()
    assert body["id"] == 1  # 空库上的第一本，自增 id 从 1 开始
    assert body["title"] == "三体"  # 响应体回带完整字段（03.4 响应模型的意识）
    assert body["rating"] == 4.5


# ============ 4、GET 列表 → 200 且包含刚创建的书（03.2 路由） ============
def test_list_books_contains_created(client):
    client.post("/books", json=BOOK)
    resp = client.get("/books")
    assert resp.status_code == 200
    titles = [b["title"] for b in resp.json()["books"]]
    assert titles == ["三体"]  # 断言精确到内容，而不是只数一下条数


# ============ 5、GET 不存在的 id → 404（03.6 HTTPException） ============
def test_get_missing_book_returns_404(client):
    resp = client.get("/books/999")
    assert resp.status_code == 404
    assert resp.json()["detail"] == "图书不存在"  # HTTPException 的 detail 原样进响应


# ============ 6、POST 非法字段 → 422（03.3 Pydantic 校验） ============
def test_create_invalid_price_returns_422(client):
    resp = client.post("/books", json={**BOOK, "price": -5})
    assert resp.status_code == 422  # 校验失败发生在进路由函数之前（03.3）
    errors = resp.json()["detail"]
    assert errors[0]["loc"][-1] == "price"  # 422 能定位到出错的是哪个字段
    assert errors[0]["type"] == "greater_than"  # 连失败原因都有机器可读的名字


# ============ 7、DELETE → 204，再 GET → 404（03.4 状态码 + 03.6） ============
def test_delete_then_get_returns_404(client):
    book_id = client.post("/books", json=BOOK).json()["id"]

    resp = client.delete(f"/books/{book_id}")
    assert resp.status_code == 204  # 删除成功
    assert resp.content == b""  # 204 的语义：响应体必须为空

    assert client.get(f"/books/{book_id}").status_code == 404  # 真的删掉了


# ============ 8、parametrize：一个用例喂多组非法价格（02.7 的老朋友） ============
@pytest.mark.parametrize("bad_price", [-1, 0, "免费", "abc"])
def test_create_rejects_bad_prices(client, bad_price):
    """价格的合法域是「>0 的数字」：-1/0 撞的是 Field(gt=0)，
    '免费'/'abc' 连 float 都解析不了——不同原因，同样的 422。"""
    resp = client.post("/books", json={**BOOK, "price": bad_price})
    assert resp.status_code == 422


# ============ TODO 1：给 04.1 的数据库版接口写测试 ============
# 内存 dict 靠 reset_books() 清空，数据库版要换思路：
#   1. fixture 里改用 SQLite 内存库（sqlite:///:memory:）建表、造 session；
#   2. 用 app.dependency_overrides[get_session] = ... 把 04.1 那个 yield 依赖
#      整体换成「返回测试 session」的函数——这是 Depends（03.5）的测试专属技能：
#      业务代码一行不改，就能把真数据库偷换成测试数据库；
#   3. 写完同样断言链路：创建 → 查询 200 → 删除 → 查询 404。

# ============ TODO 2：故意写一条必失败的测试，跑红再修绿（体验 TDD） ============
# 比如 test_list_books_sorted_by_price：期望 GET /books?sort=price 按价格升序
# 返回书——app 还没有 sort 参数，先跑一遍必红；再去实现它，跑到绿。
# 红（测试失败）→ 写实现 → 绿（测试通过）：先写测试再写实现，就是 TDD 的循环。
