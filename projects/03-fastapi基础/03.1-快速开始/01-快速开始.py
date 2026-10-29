"""03.1 快速开始：第一个 API 与自动文档

三个角色：装饰器定「HTTP 方法 + 路径」，函数定「怎么处理」，返回值就是「响应体」。

运行（不能用 python 直接跑！它只会定义 app，不会起服务）：
    uv run fastapi dev "03.1-快速开始/01-快速开始.py"
然后浏览器打开 http://127.0.0.1:8000/docs 边看边学。

修复报错from fastapi import FastAPI 无法解析导入“fastapi”
Ctrl+Shift+P → Python: Select Interpreter → 选 .\\projects\\03-fastapi基础\\.venv\\Scripts\\python.exe（只需这一次）
"""

from fastapi import FastAPI

app = FastAPI(title="我的第一个 API")  # title 会显示在 /docs 页面标题上


# ============ 演示 1：最小路由 ============
@app.get("/")
def root() -> dict:
    """访问 / 时执行；返回 dict 自动变成 JSON。这行 docstring 会出现在 /docs 里。"""
    return {"message": "你好，FastAPI"}


# ============ 演示 2：多个路由与不同返回类型 ============
@app.get("/items")
def list_items() -> list[dict]:
    """返回列表同样自动 JSON 化。"""
    return [
        {"name": "三体", "price": 45.0},
        {"name": "活法", "price": 39.9},
    ]


@app.get("/hello/{name}")
def greet(name: str) -> dict:
    """路径参数先睹为快：{name} 会作为参数传进来，注解 str 就是它的类型（03.2 细讲）。"""
    return {"hello": name}


# ============ TODO 1：最小闭环 ============
# TODO 1：加一个 GET /ping 路由，返回 {"pong": True}。
#   写完保存（fastapi dev 自动重载），分别在浏览器访问 /ping、在 /docs 里找到它。
@app.get("/ping")
def ping() -> dict:
    """访问 /ping 时执行；返回 {"pong": True}。"""
    return {"pong": True}


# ============ TODO 2：返回自己的信息 ============
# TODO 2：加一个 GET /about 路由，返回介绍自己的 dict（至少 3 个键：
#   name、goal、favorite_lang），写上 docstring。
#   完成后到 /docs 点开这个接口，确认 docstring 和返回结构都出现了——
#   体会「文档是注解的影子」。
@app.get("/about")
def about() -> dict:
    """返回关于我的信息，包括姓名、目标和最喜欢的编程语言。"""
    return {
        "name": "张三",
        "goal": "成为一名优秀的后端开发工程师",
        "favorite_lang": "Python",
    }


# ============ TODO 3：观察题 ============
# TODO 3：分别打开 /docs 和 /redoc，用一句话写下两者的区别（写在下面）：
#   答：在/docs界面上，接口文档以交互式的方式展示，用户可以直接测试API；
# 而在/redoc界面上，接口文档以静态的方式展示，更注重文档的结构和可读性。
