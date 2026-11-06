# 04.1 数据库集成

> 数据放 Python 变量里，重启就清零。ORM：定义类=建表、操作对象=读写行。SQLModel = Pydantic + SQLAlchemy，校验与建表一个类全包（03.3 老本行）。

## 知识点速查

### 1. ORM 是什么、为什么要用
对象关系映射（ORM）：把「表 → 类、行 → 对象、列 → 字段」翻译一遍。
- 不用手拼 SQL 字符串：`select(Book)` 是类型安全的查询，写错字段名立刻报错。
- 换数据库（SQLite → PostgreSQL）基本只改连接字符串，模型代码不动。

### 2. SQLModel 的双重身份（table=True 的意义）

```python
class BookBase(SQLModel):            # 公共字段 + 校验规则，只写一遍
    title: str = Field(min_length=1)
    price: float = Field(gt=0)

class Book(BookBase, table=True):    # 表模型：真表，多出 id 主键
    id: int | None = Field(default=None, primary_key=True)

class BookCreate(BookBase):          # 请求模型：不含 id——主键轮不到客户端定
    pass

book = Book.model_validate(data)     # 请求模型 → 表模型（03.3 的老朋友）
```

- 不加 `table=True`：纯校验/序列化模型（03.3 / 03.4 的本职）。
- 加 `table=True`：类映射一张表；`int | None` 的含义是「入库前没有 id，数据库填」。

### 3. engine 与 session 的生命周期

```python
engine = create_engine(f"sqlite:///{DB_PATH}")  # 连接工厂：模块级，全应用只 1 个
SQLModel.metadata.create_all(engine)            # 建表：只建不存在的表

def get_session():
    session = Session(engine)
    try:
        yield session      # 交给路由函数用（03.5 的 yield 依赖第一次真实上岗）
    finally:
        session.close()    # 请求结束必关：路由抛 404 也不例外
```

engine 与应用同生共死；session 与请求同生共死——一个请求一个会话。

### 4. CRUD 与状态码

| 操作 | 端点 | 成功 | 资源不存在 |
| --- | --- | --- | --- |
| 增 | POST /books | 201（返回带 id 的书） | — |
| 查列表 | GET /books?skip=0&limit=10 | 200 | — |
| 查详情 | GET /books/{book_id} | 200 | 404 |
| 删 | DELETE /books/{book_id} | 204（返回 None） | 404 |

### 5. Alembic 速查表（先混脸熟，项目实战章正式上）

| 命令 | 含义 |
| --- | --- |
| `alembic init migrations` | 初始化迁移环境（配置 + 脚本目录） |
| `alembic revision --autogenerate` | 对比模型与库的现状，自动生成「改表脚本」 |
| `alembic upgrade head` | 把未执行的迁移依次应用到最新 |
| `alembic downgrade -1` | 回滚上一个版本（改错了能后悔） |

本章先用 `create_all` 跑通——它只建不存在的表，**不改已有表结构**，所以 TODO 3 加字段看不到效果。

## 易错点
- 忘了 `commit()`：`add` 只是入队，`commit` 才写库——「明明执行成功了，怎么没保存」十有八九是它；要拿自增 id 还得再 `refresh()`。
- session 不关：连接泄漏，SQLite 文件被占着，后续请求开不了会话。交给 yield 依赖的 teardown 管，别在路由里手动开会话。
- SQLite 的 `check_same_thread`：默认连接只许创建线程用，而 FastAPI 同步路由在线程池里会换线程，不放开就报错。这是 SQLite 特有配置，不是所有库都需要。
- 把表模型直接当响应：今天 Book 没有秘密，明天加了 `is_deleted`、`hashed_password` 就全泄漏出去——03.4 的白名单思想，响应模型的字段清单说了算。

## 进阶提示
- `session.get(Book, id)` 按主键查是捷径；复杂条件用 `select(Book).where(...)`。
- 分页用 `.offset(skip).limit(limit)`：是数据库挑行，不是拉全表回 Python 再切片。
- 「入参 BookCreate / 表 Book / 出参 BookPublic」三件套是官方推荐分层，项目实战章照此组织。

## 学习顺序与练习

启动命令（在 projects/04-fastapi进阶 目录下）：

`uv run fastapi dev "04.1-数据库集成/01-数据库.py"`

先建书 → 重启 → 再查，亲眼看「持久化」。然后完成 TODO：

1. TODO 1：GET /books 加可选 `author` 过滤（`.where(Book.author == author)`）。
2. TODO 2：PATCH /books/{book_id} 只改价格——PriceUpdate 白名单模型，200 / 404 自己定清楚。
3. TODO 3：思考题——加字段后表结构为何不变？带着问题读第 5 节，完整答案在项目实战章。
