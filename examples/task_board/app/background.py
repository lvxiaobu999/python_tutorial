"""M5 · 后台任务函数——通知的真正执行者（04.4）

⭐ 本作业最重要的工程细节藏在这里：

任务函数**必须自己开 session**，不能复用请求的 session——
请求的 session 由 yield 依赖管理，生命周期跟着请求走；而后台任务在「响应发送完之后」
才执行，属于请求之外的世界（哪个请求的 session 归哪个请求，任务不该去借）。

    def notify_assignment(to_username: str, task_title: str) -> None:
        with Session(engine) as session:      # 自己的 session，自己关
            ...

登记方（tasks.py 的 PATCH）只写一句：tasks.add_task(notify_assignment, assignee用户名, 任务标题)
——传函数本身 + 参数（04.4 坑 1：写成调用就当场执行了）。

通知内容规格：message 里必须包含任务标题（验收测试按这个断言）。
"""

from sqlmodel import Session

from app.database import engine


def notify_assignment(to_username: str, task_title: str) -> None:
    """给被分配人写一条通知（响应发送完之后才执行）。"""
    raise NotImplementedError("M5：自己开 session → 按用户名查到人 → add Notification → commit")
