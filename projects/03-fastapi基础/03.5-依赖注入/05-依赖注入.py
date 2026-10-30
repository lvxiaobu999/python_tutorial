"""03.5 依赖注入：公共逻辑只写一遍

同一个查询参数组合、同一段「取当前用户」逻辑要被多个接口共用时，
抽成依赖函数，用 Depends 声明——FastAPI 负责调用和传参。

运行（在 projects/03-fastapi基础 目录下）：
    uv run fastapi dev "03.5-依赖注入/05-依赖注入.py"
对照 /docs 观察：依赖的参数是怎么变成各接口的查询参数的。
"""

from typing import Annotated

from fastapi import Depends, FastAPI

app = FastAPI(title="03.5 依赖注入练习")


# ============ 演示 1：把公共查询参数抽成依赖 ============
def pagination(skip: int = 0, limit: int = 10) -> dict:
    """这些参数会自动成为「使用这个依赖的每个接口」的查询参数。"""
    return {"skip": skip, "limit": limit}


Page = Annotated[dict, Depends(pagination)]  # 起个短名字，多处复用更清爽


@app.get("/books")
def list_books(page: Page) -> dict:
    """/books?skip=2&limit=5——分页逻辑只写了一遍，两个接口都在用。"""
    return {"数据源": "图书表", **page}


@app.get("/reviews")
def list_reviews(page: Page) -> dict:
    """同一个 Page 依赖直接复用：路由函数只声明「我需要分页」，不关心实现。"""
    return {"数据源": "评论表", **page}


# ============ 演示 2：依赖链——依赖也可以依赖别人 ============
def fake_token_check(token: str = "") -> dict:
    """第一层：解析 token。真实项目里这里是 JWT 校验（04.2 见）。"""
    users = {
        "admin-token": {"user": "张三", "role": "admin"},
        "guest-token": {"user": "访客", "role": "guest"},
    }
    return users.get(token, {"user": "匿名", "role": "guest"})


def require_admin(user: Annotated[dict, Depends(fake_token_check)]) -> dict:
    """第二层：基于第一层的结果再判断——依赖可以套依赖。
    正式写法里非 admin 应抛 403（HTTPException，03.6 见），这里先优雅降级。"""
    return {**user, "allowed": user["role"] == "admin"}


@app.get("/admin-dashboard")
def admin_dashboard(user: Annotated[dict, Depends(require_admin)]) -> dict:
    """/admin-dashboard?token=admin-token → allowed=true；
    换 guest-token 或不传 → allowed=false。三层函数各管一层。"""
    return user


# ============ 演示 3：yield 依赖：前逻辑 + 后逻辑 ============
def fake_db_session():
    """yield 之前是 setup（请求前），之后是 teardown（响应后）——02.3 生成器的老朋友。"""
    print("→ [依赖] 打开连接")
    yield "conn-1"
    print("← [依赖] 关闭连接")


@app.get("/db-info")
def db_info(conn: Annotated[str, Depends(fake_db_session)]) -> dict:
    """访问一次这个接口，然后看运行 fastapi dev 的终端：两行 print 的顺序就是生命周期。"""
    return {"连接": conn}


# ============ TODO 1：排序依赖 ============
# 写依赖函数 sort_options(sort_by: str = "title")，把它和 Page 组合，
#   加 GET /shelf/books：同时收到分页和排序两个查询参数并原样返回。


# ============ TODO 2：用到大作业 ============
# 加 GET /library/books（期末大作业的图书列表）：复用 Page 依赖，返回 {"books": [...], "skip": ..., "limit": ...}。


# ============ TODO 3：依赖链练习 ============
# 写依赖 valid_page，它 Depends(pagination) 拿到结果后强制 limit ≤ 50（超了就改成 50），
#   让 /library/books 改用它，试 ?limit=999 看是否被拦到 50。
