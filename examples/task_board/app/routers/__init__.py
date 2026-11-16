"""路由包：routers/ 下每个模块各持有一个 APIRouter 实例，由 main.py 统一挂载。

不在 __init__.py 里做别名转发（如 from .users import router as users_router）：
main.py 的挂法是「from app.routers import users → users.router」，全项目一种挂法。
__init__ 里的预加载还会让「任何 import app.routers」都连带执行 users.py，
路由一多，循环导入的风险也随之变大——保持这个文件为空最稳。
"""
