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

from fastapi import APIRouter

from app.database import SessionDep
from app.models import User
from app.schemas import RegisterIn
from app.security import hash_password

router = APIRouter(tags=["users"])


@router.post("/register")
def register(body: RegisterIn, session: SessionDep):
    hash_pws = hash_password(body.password)
    user = User.model_validate(body)
    session.add(user)
    session.commit()
    session.refresh(user)
    return user
