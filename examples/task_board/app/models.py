"""M1 · 表模型——你的第一块拼图（04.1：一个类身兼两职）

全部 5 张表的字段规格见 README「数据模型」节，本文件是它的代码落地。

【本项目的权威写法 = SQLModel，不是裸 SQLAlchemy】
- main.py / tests/conftest.py 的建表入口是 `SQLModel.metadata.create_all(engine)`——
  模型必须继承 SQLModel 且 table=True，才会注册进 SQLModel.metadata 被建出来；
- SQLAlchemy 2.0 的 `DeclarativeBase` 也是业内权威写法，但它注册进自己的 Base.metadata，
  和 SQLModel.metadata 是两本没交集的账：混用的结果就是 create_all 空转、
  全套测试永远报「no such table」。SQLModel 本身就是套在 SQLAlchemy 2.0 类型化
  写法（Mapped/mapped_column）外面的一层皮——学它不亏，跟着项目地基走就行。

【本文件的写法约定速查】
- id 统一 `int | None = Field(default=None, primary_key=True)`——主键由数据库自增，
  客户端创建时轮不到传（03.4 白名单思想）；
- 外键统一 `Field(foreign_key="表名.字段")`——引号里是「表名.字段」，表名 = 类名小写
  （README/GUIDE 约定；SQLModel 不写 __tablename__ 时，默认表名就是类名小写，
  手写 __tablename__ 会触发 Pylance 已知误报，索性不写）；
- 「可空外键」统一 `int | None = Field(default=None, foreign_key=...)`——
  「还没分配」是正常状态，NULL 是合法值不是错误；
- 唯一性约束只给业务明确要求的字段（username），不做默认直觉；
- 每张表都带 created_at（README 加分项 3 提前落了）。

⚠️ 本文件完成后，「no such table」的红就会褪去，露出下一层业务红——TDD 一层层揭。
"""

from datetime import datetime, timezone

from sqlmodel import DateTime, Field, SQLModel, Text


class User(SQLModel, table=True):
    """用户表 user：注册/登录/身份。继承写法固定为 `(SQLModel, table=True)`。"""

    # 主键：数据库自增。int | None 的 None 表示「还没入库」——入库后由数据库填。
    id: int | None = Field(default=None, primary_key=True)

    # 登录凭证：登录就是按 username 找人，重名会「顶号」——唯一性是业务明说的，
    # 所以才加 unique=True（对照 Board.name：业务没要求唯一，就不加）。
    # max_length=50 → 建表时是 VARCHAR(50)，请求模型（schemas）再挡一层长度校验。
    username: str = Field(max_length=50, unique=True)

    # 只存 bcrypt 哈希、绝不存明文（04.2）。命名对齐 README 与 schemas.py 的白名单
    # （UserPublic 响应模型绝不含 password_hash，03.4）。bcrypt 哈希固定 60 字符，
    # 255 留了换算法的余量——改列宽要动 Alembic 迁移，宁长勿短。
    password_hash: str = Field(max_length=255)

    # "admin" | "member"。「第一个注册的用户自动升 admin」是业务规则，
    # 落在 M2 的注册路由里；表只负责存，默认值给最普通的那档。
    # 合法值校验放在门口（schemas 用 Literal），不靠数据库 CHECK——门口校验思想。
    role: str = Field(default="member", max_length=20)

    # 时间戳小坑（README 加分项 3 说的就是它）：
    # - 不能写 default=datetime.now()——括号一加，值在 import 时刻就算好了，
    #   全表共用同一个快照；default_factory 传「函数本身」，每次建对象时现算；
    # - utcnow() 在 Python 3.12+ 已弃用，现算 UTC 用 now(timezone.utc)；
    # - SQLite 存取会丢时区标记（存的是 UTC 墙上时间），timezone=True 为换 Postgres 预留。
    created_at: datetime = Field(
        default_factory=lambda: datetime.now(timezone.utc),
        sa_type=DateTime(timezone=True),
    )


class Board(SQLModel, table=True):
    """看板表 board：任务的「房间」——WS 广播、SSE 回放都以它为单位。"""

    id: int | None = Field(default=None, primary_key=True)

    # API 返回 {id, name}（README 规格节 + conftest 发 {"name": ...}），所以叫 name。
    # 不加 unique：两块板都叫「开发计划」完全合法；「唯一」要业务明说才加。
    name: str = Field(max_length=50)

    created_at: datetime = Field(
        default_factory=lambda: datetime.now(timezone.utc),
        sa_type=DateTime(timezone=True),
    )


class Task(SQLModel, table=True):
    """任务表 task：看板里的一张卡片，状态机 todo → doing → done。"""

    id: int | None = Field(default=None, primary_key=True)

    # 外键 → board.id。index=True 是外键列的标配：GET /tasks?board_id=... 全按它过滤，
    # 没索引就是全表扫描。「板不存在」的 404 由路由先查后建来保证，两层都要有。
    board_id: int = Field(foreign_key="board.id", index=True)

    # 不加 unique：不同板可以有同名任务，改名也不该被拦。
    title: str = Field(max_length=50)

    # 长文本用 Text（VARCHAR 有长度上限）。字段名对齐规格：description，不是 content
    # （测试断言 body["description"]）。
    description: str = Field(sa_type=Text)

    # 新任务默认 todo（test_create_task_defaults 断言）。合法值 "todo"|"doing"|"done"
    # 由 schemas.py 的 Literal 在门口把关；「只能前进、后退 409」是路由里的状态机判断。
    status: str = Field(default="todo", max_length=10)

    # 可空外键：None = 还没分配（正常状态）。int | None + default=None 是关键写法——
    # POST /tasks 不传 assignee_id 时，响应里就是 null（测试明确断言了这一点）。
    # index=True 同理：GET /tasks?assignee_id=... 按它过滤。
    assignee_id: int | None = Field(default=None, foreign_key="user.id", index=True)

    # 进阶提示（现在刻意不写，README M1 约定「暂时不需要」）：
    # 1. ondelete="CASCADE"（删板自动删任务）——你的直觉很好，但 SQLite 默认不开启
    #    PRAGMA foreign_keys，约束压根不生效；且 SQLModel 的 Field(foreign_key=...)
    #    不支持该参数，要写就得 sa_column=Column(ForeignKey(..., ondelete="CASCADE"))。
    #    等切 Postgres 时再上不迟。
    # 2. relationship()（对象级联取数）——M1 全靠显式按 id 查，以后想要再说。
    created_at: datetime = Field(
        default_factory=lambda: datetime.now(timezone.utc),
        sa_type=DateTime(timezone=True),
    )


class Notification(SQLModel, table=True):
    """通知表 notification：后台任务写入的「收据」（04.4）。

    GET /notifications 返回本人通知、新的在前——按 id 降序即可，路由层的事。
    """

    id: int | None = Field(default=None, primary_key=True)

    # 通知是发给「人」的：user_id → user.id，加索引（按人查信箱是唯一读路径）。
    user_id: int = Field(foreign_key="user.id", index=True)

    # 规格刻意不含 task_id 外键：message 里直接冗余一份任务标题（background.py 负责拼，
    # 测试断言「任务标题」 in message）。这叫「反范式」：任务删了，通知这张收据还能独立
    # 读懂，用一点冗余换解耦——原稿把 ForeignKey("tasks.id") 挂在 title 上属于两概念打架。
    message: str = Field(sa_type=Text)

    created_at: datetime = Field(
        default_factory=lambda: datetime.now(timezone.utc),
        sa_type=DateTime(timezone=True),
    )


class Activity(SQLModel, table=True):
    """活动流水表 activity：任务增/改/删时【同步】写入；SSE 回放它（M6）。

    和 Notification 的对照是本作业的设计判断题：Activity 要被 SSE 现刻回放 → 同步写；
    Notification 用户不必等 → 后台写。表结构长得像，写入时机天差地别。
    """

    id: int | None = Field(default=None, primary_key=True)

    # 流水挂在板上。index=True：SSE 只回放「这一块板」的流水。
    board_id: int = Field(foreign_key="board.id", index=True)

    # 一句人话流水，如 "alice 把「修登录页」移到 doing"——SSE 逐条 data: {...} 推给前端。
    # 回放取最近 ≤20 条、按 id 正序（新写入的 id 大），路由层 order_by 的事。
    message: str = Field(sa_type=Text)

    created_at: datetime = Field(
        default_factory=lambda: datetime.now(timezone.utc),
        sa_type=DateTime(timezone=True),
    )
