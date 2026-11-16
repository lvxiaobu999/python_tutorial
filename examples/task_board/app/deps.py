"""M2 · 依赖层——「谁能进来」的守门员（04.2 依赖链的工程版）

依赖链：oauth2_scheme（抠 token）→ get_current_user（decode + 查库）→ require_admin（比对角色）
与 04.2 的对应关系一模一样，只是搬进了独立模块、被多个 router 共享。

给 router 用的 Annotated 别名也要你定义（在函数实现完之后）：
    CurrentUser  = Annotated[User, Depends(get_current_user)]
    AdminUser    = Annotated[User, Depends(require_admin)]
（User 在 M1 的 models.py 里——别名定义放它后面，import 顺序才不会断。）

细节提示：
- oauth2_scheme 已给出：tokenUrl="login" 是说给 /docs 听的（右上角 Authorize 按钮）；
- get_current_user：decode_token 抛出任何异常 → 401「token 无效或已过期」；
  查无此人（token 合法但用户已删）→ 同样 401——权限以库为准；
- require_admin：user.role != "admin" → 403「需要管理员权限」（401 是没登录，403 是没权限）。
"""

from typing import Annotated

from fastapi import Depends
from fastapi.security import OAuth2PasswordBearer

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="login")

TokenDep = Annotated[str, Depends(oauth2_scheme)]


def get_current_user(token: TokenDep):
    raise NotImplementedError("M2：decode → 查库 → 401 / 返回用户（对照 04.2 get_current_user）")


def require_admin(user):
    raise NotImplementedError("M2：非 admin 抛 403（对照 04.2 require_admin）")
