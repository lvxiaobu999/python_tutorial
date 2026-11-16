"""M2 · 用户路由——注册 / 登录 / 我是谁（04.2 全套 + APIRouter 新排布 03.2）

端点规格（详细字段见 README「API 规格」节）：
- POST /register   201 → UserPublic；用户名重复 → 400
                    ⭐ 业务规则：第一个注册的用户自动 role="admin"（后续都是 member）
                    ——没有「种管理员」的脚本时，这是最简单的 bootstrap 设计
- POST /login      200 → {"access_token", "token_type": "bearer"}；密码错 → 401
                    收 OAuth2PasswordRequestForm（表单不是 JSON，OAuth2 规范）
                    登录失败给同一句话——不向攻击者暗示「这个用户名存在」
- GET /me          200 → UserPublic；没带 token → 401（oauth2_scheme 自动拦）

写法提示：
- 查用户名是否已存在：select(User).where(User.username == ...)，记得接住返回值（04.1 坑 2）；
- /me 的返回类型标注 UserPublic——password_hash 就算在内存里也绝不出口（03.4 白名单）。
"""

from fastapi import APIRouter, HTTPException, status
from sqlmodel import select

from app.database import SessionDep
from app.models import User
from app.schemas import RegisterIn, UserPublic
from app.security import hash_password

router = APIRouter(tags=["users"])


@router.post("/register", status_code=status.HTTP_201_CREATED)
def register(body: RegisterIn, session: SessionDep) -> UserPublic:
    """注册：查重 → 哈希入对象 → 首用户升 admin → 白名单出口。

    四步各有 why（对照 04.1 / 03.6 / 03.4）：
    1. 查重给 400（业务冲突），而不是等 username 的 UNIQUE 约束在 INSERT 时炸成 500；
    2. 哈希必须先算好再建 User——RegisterIn 没有 password_hash 字段，
       model_validate(body) 会直接 ValidationError（你刚撞的那堵墙）；
    3. 「第一个注册的用户是 admin」= 注册时查一下表里有没有人，空表即首任；
    4. 返回注解 UserPublic 是白名单：FastAPI 按它的字段清单逐个挑，
       password_hash 就算在内存里也出不了门。
    """
    # 查重：select 链式方法返回「新的查询对象」，必须接住返回值（04.1 坑 2）
    existing = session.exec(select(User).where(User.username == body.username)).first()
    if existing is not None:
        raise HTTPException(status_code=400, detail="用户名已被注册")

    # 显式传字段建对象：明文密码只在这行被哈希，models.User 里永远只有哈希
    user = User(username=body.username, password_hash=hash_password(body.password))

    # 首用户 bootstrap：此时表里还没插任何人，查到空 = 我是第一个
    if session.exec(select(User)).first() is None:
        user.role = "admin"

    session.add(user)  # 入队（04.1 老三样）
    session.commit()  # 落库；id 由数据库自增生成
    session.refresh(user)  # commit 后属性被清出内存，回填 id 等（04.1 expire_on_commit 坑）
    # 出口显式转换：User 表对象 → UserPublic 响应模型（白名单逐字段挑）。
    # 为什么不直接 return user？FastAPI 运行时确实会按返回注解隐式过滤，
    # 但 Pylance 是静态检查、只认继承关系——User 和 UserPublic 互不隶属，
    # 「User 不可分配给 UserPublic」就是这么来的。model_validate 一行两边都认。
    return UserPublic.model_validate(user)
