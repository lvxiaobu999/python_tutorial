"""04.2 认证与授权：bcrypt 哈希 + JWT 签发校验 + 依赖保护路由

03.5 的 fake_token_check 是「拿字典假装 token」，这次来真的：
密码不存明文存哈希（bcrypt，不可逆），身份不靠猜靠签名（JWT，改一字就露馅）。

运行（在 projects/04-fastapi进阶 目录下）：
    uv run fastapi dev "04.2-认证与授权/02-认证.py"
对照 /docs 观察：点右上角 Authorize 登录后，带锁接口自动带上 Authorization 头（03.4 Header 的真用场）。
"""

import time
from typing import Annotated

import bcrypt
import jwt
from fastapi import Depends, FastAPI, HTTPException, status
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from pydantic import BaseModel

app = FastAPI(title="04.2 认证与授权练习")

# 真实项目：密钥从环境变量读（os.environ），写死进代码并提交 git = 任何人都能伪造 token
SECRET_KEY = (
    "dev-only-secret-change-me-please-32bytes!"  # HS256 密钥建议 ≥32 字节（RFC 7518）
)
ALGORITHM = "HS256"  # 签名算法：同一把密钥既用来签发也用来校验（对称签名）
ACCESS_TOKEN_EXPIRE = 2  # token 有效期（秒）；TODO 2 会改成 1 亲眼看过期


# ============ 演示 1：密码哈希——存「指纹」，不存密码 ============
def hash_password(plain: str) -> str:
    """哈希单向不可逆（加密双向可解），只能「验」不能还原；
    gensalt 随机盐让同一密码两次哈希都不同，彩虹表（预计算指纹库）失效。"""
    return bcrypt.hashpw(plain.encode(), bcrypt.gensalt()).decode()


@app.post("/hash-demo")
def hash_demo(password: str) -> dict:
    """同一密码哈希两次：结果不同（随机盐），但 checkpw 都能验通过——「验」不靠还原。"""
    h1, h2 = hash_password(password), hash_password(password)
    return {
        "同一密码两次哈希不同": h1 != h2,
        "checkpw 验对密码": bcrypt.checkpw(password.encode(), h1.encode()),
        "checkpw 验错密码": bcrypt.checkpw("猜的密码".encode(), h1.encode()),
    }


# ============ 演示 2：注册 + 登录——哈希入库，签发 JWT ============
fake_users_db: dict[str, dict] = (
    {  # 真实项目：这是数据库的 user 表；内存 dict 重启即丢，仅作练习
        "zhang": {
            "username": "zhang",
            "role": "admin",
            "password_hash": hash_password("admin123"),
        },
        "li": {
            "username": "li",
            "role": "reader",
            "password_hash": hash_password("reader123"),
        },
    }
)


class RegisterIn(BaseModel):  # 请求体校验是 03.2 Pydantic 的老朋友
    username: str
    password: str


@app.post("/register", status_code=201)  # 建资源返回 201，03.4 状态码
def register(body: RegisterIn) -> dict:
    if body.username in fake_users_db:
        raise HTTPException(status.HTTP_400_BAD_REQUEST, detail="用户名已被注册")
    fake_users_db[body.username] = {
        "username": body.username,
        "role": "reader",
        "password_hash": hash_password(body.password),  # 入库的只有哈希，没有明文
    }
    return {"欢迎": body.username}


def create_token(username: str) -> str:
    """payload 只放「谁」（sub）和「活到几点」（exp）——绝不放密码等敏感信息。"""
    payload = {"sub": "zhangsan", "exp": int(time.time()) + ACCESS_TOKEN_EXPIRE}
    return jwt.encode(payload, SECRET_KEY, algorithm=ALGORITHM)


@app.post("/login")
def login(form: Annotated[OAuth2PasswordRequestForm, Depends()]) -> dict:
    """收表单（x-www-form-urlencoded）而非 JSON——OAuth2 规范如此；/docs 的 Authorize 弹窗正是往这里发表单。"""
    user = fake_users_db.get(form.username)
    ok = user and bcrypt.checkpw(form.password.encode(), user["password_hash"].encode())
    if not ok:
        # 用户不存在 / 密码错误给同一句话：不向攻击者暗示「这个用户名是存在的」
        raise HTTPException(status.HTTP_401_UNAUTHORIZED, detail="用户名或密码错误")
    return {"access_token": create_token(form.username), "token_type": "bearer"}


# ============ 演示 3：get_current_user——03.5 假 token 的真身 ============
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="login")
# 只干一件事：从请求头 Authorization: Bearer xxx 抠出 token（03.4 Header 的自动化版），没带就 401；
# tokenUrl="login" 是说给 /docs 听的：「token 去 POST /login 换」——于是右上角有了 Authorize 按钮。


def get_current_user(token: Annotated[str, Depends(oauth2_scheme)]) -> dict:
    """依赖链真实版：oauth2_scheme 抠 token → jwt.decode 验签名与过期 → 查库取用户。"""
    try:
        payload = jwt.decode(
            token, SECRET_KEY, algorithms=[ALGORITHM]
        )  # 必须显式验算法；exp 到期也一并拦
    except jwt.InvalidTokenError:  # 签名不对 / 已过期 / 格式损坏，统统进这里
        raise HTTPException(status.HTTP_401_UNAUTHORIZED, detail="token 无效或已过期")
    user = fake_users_db.get(
        payload["sub"]
    )  # 权限以库为准：token 只带名字，改角色不用重登
    if user is None:
        raise HTTPException(status.HTTP_401_UNAUTHORIZED, detail="用户不存在")
    return user


@app.get("/me")
def me(user: Annotated[dict, Depends(get_current_user)]) -> dict:
    """先点右上角 Authorize 登录再访问：OAuth2 → decode → 查库 → 返回你。"""
    time.sleep(1)
    return user


# ============ 演示 4：require_admin——认证之上再做授权 ============
def require_admin(user: Annotated[dict, Depends(get_current_user)]) -> dict:
    """03.5 版本只标记 allowed 不拦截；这次身份是真的，非 admin 直接 403（03.6 HTTPException）。"""
    if user["role"] != "admin":
        raise HTTPException(status.HTTP_403_FORBIDDEN, detail="需要管理员权限")
    return user


BOOKS = [  # cost 是内部进货成本，绝不从公开接口漏出去
    {"id": 1, "title": "三体", "price": 23.0, "cost": 12.5},
    {"id": 2, "title": "活着", "price": 20.0, "cost": 11.0},
]


@app.get("/books")
def list_books() -> dict:
    """公开接口：谁都能看，但只给售价。"""
    return {
        "books": [
            {"id": b["id"], "title": b["title"], "price": b["price"]} for b in BOOKS
        ]
    }


@app.get("/admin/books")
def admin_books(user: Annotated[dict, Depends(require_admin)]) -> dict:
    """li（reader）→ 403；zhang（admin）→ 连成本一起看。认证回答「你是谁」，授权回答「你能看吗」。"""
    return {"books": BOOKS, "查看人": user["username"]}


# ============ TODO 1：给删除接口上管理员保护 ============
# 写 DELETE /books/{book_id}，叠 require_admin 依赖：删除成功返回 {"deleted": book_id}，
#   书不存在抛 404（03.6）。自测三连：匿名 → 401，li（reader）→ 403，zhang（admin）→ 200。
@app.delete("/books/{book_id}")
def delete_book(book_id: int, user: Annotated[dict, Depends(require_admin)]) -> dict:
    """删除图书列表接口,只有管理员有删除权限"""
    book = next((b for b in BOOKS if b["id"] == book_id), None)

    if book is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"id={book_id} 的书本找不到",
        )

    BOOKS.remove(book)
    return {"deleted": book_id}


# ============ TODO 2：亲眼看「过期」 ============
# 把 ACCESS_TOKEN_EXPIRE 改成 1，重启后重新登录拿新 token，睡 2 秒再访问 /me：
#   token 没被改过一个字节，但时间到了——观察这次的 401（jwt.ExpiredSignatureError）。


# ============ TODO 3：亲眼看「签名」 ============
# 把 token 第三段（signature）或中间 payload 段（比如把 sub 改成 zhang）随便改几个字符再访问 /me：
#   服务器用 SECRET_KEY 对前两段重算签名、对不上就拦——改一个字节都骗不过，观察 401。
