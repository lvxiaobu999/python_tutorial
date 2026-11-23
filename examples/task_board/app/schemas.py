"""M2/M3 · 请求与响应模型——和表模型分开的「门口模型」（03.3 / 03.4）

需要的模型（字段规格见 README「API 规格」节）：
- RegisterIn：username / password（POST /register 的请求体）
- UserPublic：id / username / role——注意：**绝不含 password_hash**（03.4 响应模型白名单）
- TaskCreate / TaskUpdate / TaskPublic
- status 字段用 Literal["todo", "doing", "done"] 限定（03.5 笔记踩过：别写 "todo" | "doing" 联合类型，
  静态检查器认、运行时 TypeError）

写法提示：
- TaskUpdate 所有字段都可省（PATCH 语义：只改带来的字段）——配合 exclude_unset 使用；
- TaskPublic 不含任何内部字段，响应长什么样由它的字段清单说了算。
"""

from sqlmodel import Field, SQLModel

# ==================== TODO M2 · 用户部分（现在写，验收 = test_users 7 passed） ====================

# TODO 2.1 RegisterIn —— POST /register 的请求体
#   字段：
#   - username: str —— max_length 对齐 user 表列（50）：门口先挡超长，
#     别等 INSERT 撞数据库的 VARCHAR(50) 才报错；重名 400 不归模型管（路由查库判断）
#   - password: str —— 明文只过门口、只被哈希（04.2）。给个 min_length 挡空串即可，
#     别把门设得比规格严（测试统一密码 pw123456，8 位；设 min_length=10 会让全套测试假红）

# TODO 2.2 UserPublic —— 注册/登录后「用户是什么」的响应模型
#   字段：id: int / username: str / role: str ——就这三个。
#   - id 敢写 int 而不是 int | None：能出门的用户都已入库、必有主键（门口和仓库状态一致）
#   - 字段清单 = 白名单：password_hash 就算躺在 user 对象内存里，
#     不在清单里就出不了门（03.4；test_user_public_shape_hides_password_hash 的断言正是 keys 恰好三个）
#   思考题（写完回头看）：路由里 return 的是 models.User 对象（带 password_hash），
#   为什么响应 JSON 里没有它？——FastAPI 按返回类型注解逐字段过滤，多的一律扣下。

# ==================== TODO M3 · 任务部分（进 M3 再回来写，现在留空） ====================
# TODO M3：TaskCreate / TaskUpdate / TaskPublic
#   ——规格看本文件顶部 docstring + README「API 规格」节；TaskUpdate 全字段可省是 PATCH 的灵魂


class RegisterIn(SQLModel):
    """POST /register 的请求体——「进门白名单」：客户端允许提交的只有这两个字段。"""

    # 门口挡超长（对齐 user 表的 VARCHAR(50)）：超长请求 422，而不是等 INSERT 撞库才炸。
    # 「用户名重复 → 400」不归模型管——那是查库后的业务判断，路由层的事。
    username: str = Field(max_length=50)

    # 只挡空串（min_length=1）。规格没定密码强度，校验要跟需求对齐，不是越严越专业：
    # 设 min_length=8 也能过（测试密码 pw123456 恰好 8 位），设 10 全套测试假红。
    password: str = Field(min_length=1)


class UserPublic(SQLModel):
    """「出门白名单」：用户是什么，由这三个字段说了算（03.4）。"""

    # id 敢写 int：能出门的用户都已入库、必有主键——未入库对象（id=None）
    # 在这里直接被拒（实测验证过），这就是「门口和仓库状态一致」。
    id: int

    # 镜像表列 VARCHAR(50)：出口再验一道。上游（RegisterIn + 库）已保证 ≤50，
    # 这行是保险不是关口——上游若失控，会在出口 500 而不是静默放出脏数据。
    username: str = Field(max_length=50)

    # 角色值由路由的业务规则写（第一个注册者 admin、其余 member），模型只管形状。
    # 进阶可选：Literal["admin", "member"] 能把出口锁死并自文档化，
    # 代价是加第三种角色时要同步改这里——现阶段 str 足够。
    role: str


class BoardCreate(SQLModel):
    """POST /boards 请求体——门口只放客户端允许提交的 name。"""

    # 长度对齐 board 表列 VARCHAR(50)，超长 422 在门口拦下
    name: str = Field(max_length=50)


class BoardPublic(BoardCreate):
    """看板的对外形状：{id, name}（README API 规格）。

    命名跟随项目惯例 XxxPublic（UserPublic / TaskPublic 同族）：
    「Public」= 出口形状，与门口的 In / 表模型三兄弟一眼区分开。
    继承 BoardCreate 复用 name 约束；id 敢写 int，理由同 UserPublic——
    能出门的板都已入库、必有主键。
    """

    id: int
