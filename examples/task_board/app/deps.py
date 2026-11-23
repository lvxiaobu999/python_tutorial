"""M2 · 依赖层——「谁能进来」的守门员（04.2 依赖链的工程版）

依赖链：oauth2_scheme（抠 token）→ get_current_user（decode + 查库）→ require_admin（比对角色）
与 04.2 的对应关系一模一样，只是搬进了独立模块、被多个 router 共享。

给 router 用的两个别名（紧跟各自依赖的实现定义——注解在 def 时立即求值，
require_admin 用到 CurrentUser，就必须先定义它，否则 NameError）：
    CurrentUser = Annotated[User, Depends(get_current_user)]   —— 需登录的端点用
    AdminUser   = Annotated[User, Depends(require_admin)]      —— 需管理员的端点用
"""

from typing import Annotated

import jwt
from fastapi import Depends, HTTPException
from fastapi.security import OAuth2PasswordBearer
from sqlmodel import select

from app.database import SessionDep
from app.models import User
from app.security import decode_token

# tokenUrl="login" 是说给 /docs 听的：右上角 Authorize 按钮按 OAuth2 规范
# 用表单向 /login 要 token，之后每个请求自动带上 Authorization: Bearer <token>
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="login")

TokenDep = Annotated[str, Depends(oauth2_scheme)]


def get_current_user(token: TokenDep, session: SessionDep) -> User:
    """依赖链第二环：decode → 查库 → 401 / 返回用户。

    两处 401 一个原则——「权限以库为准，失败信息不给死因」：
    - token 验不过（签名错 / 过期 / 格式坏）：decode_token 抛 jwt.InvalidTokenError，
      这里统一转 401。catch 范围只到这个基类——别的异常（如库挂了）不该被吞成 401；
    - token 合法但查无此人（用户被删）：同样 401——旧 token 不能因为人没了继续有效。
    """
    try:
        username = decode_token(token)
    except jwt.InvalidTokenError:
        raise HTTPException(status_code=401, detail="token 无效或已过期")

    user = session.exec(select(User).where(User.username == username)).first()
    if user is None:
        raise HTTPException(status_code=401, detail="token 无效或已过期")
    return user


# —— 别名紧跟实现：CurrentUser 在 require_admin 的注解里被引用，必须先定义（def 时求值）——
CurrentUser = Annotated[User, Depends(get_current_user)]


def require_admin(user: CurrentUser) -> User:
    """依赖链第三环：非 admin → 403。401 是没登录，403 是登录了但没权限——语义不同。"""
    if user.role != "admin":
        raise HTTPException(status_code=403, detail="需要管理员权限")
    return user


AdminUser = Annotated[User, Depends(require_admin)]
