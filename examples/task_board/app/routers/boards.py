"""M3 · 看板路由——任务的「房间」划分（也划定了 M6 广播的范围）

端点规格：
- POST /boards          201 → {"id", "name"}；需登录（401）
- GET /boards           200 → [{"id", "name"}...]；需登录
- DELETE /boards/{id}   204；⭐ 仅 admin（403）——require_admin 的第一个自然落点（04.2 TODO1 同款）
                        板不存在 → 404；删除成功响应体必须为空（204 的语义，03.4）

写法提示：
- 删板时要不要连带删任务？验收测试不考——想清楚即可（真项目叫级联删除，README 加分项提了）。
"""

from fastapi import APIRouter, HTTPException, status
from sqlmodel import select

from app.database import SessionDep
from app.deps import AdminUser, CurrentUser
from app.models import Board
from app.schemas import BoardCreate, BoardPublic

router = APIRouter(tags=["boards"], prefix="/boards")


@router.post("", status_code=status.HTTP_201_CREATED)
def create_board(
    current_user: CurrentUser,  # 门禁：没带/带错 token → oauth2_scheme 直接 401，函数体不执行
    body: BoardCreate,
    session: SessionDep,
) -> BoardPublic:
    """建板：登录即可（member 也行），不需要 admin——admin 权限留给删板（规格明确）。"""
    board = Board(name=body.name)

    session.add(board)  # 04.1 老三样
    session.commit()  # id 由数据库自增生成
    session.refresh(board)  # commit 后属性被清出内存，回填 id（expire_on_commit 坑）

    return BoardPublic.model_validate(board)  # 出口显式转换（同 register 的处理）


@router.get("")
def get_board_list(
    current_user: CurrentUser,  # 门禁同款：声明即触发，函数体不用它（401 在进门前发生）
    session: SessionDep,
) -> list[BoardPublic]:
    """列板：登录即可看全部（规格没有筛选参数，无条件查全部——04.1 的查列表三件套）。

    GET 与 POST 的三个不同：
    - 没有请求体参数：读操作不提交数据，BoardCreate 在这里是残留，已删；
    - 不标 status_code：GET 成功就是 200（FastAPI 默认值）；
    - 返回 list[BoardPublic]：.all() 出来的是表对象序列，逐个过出口转换。
    """
    boards = session.exec(
        select(Board)
    ).all()  # select 只建查询，exec 才执行（login 的老坑）
    return [BoardPublic.model_validate(b) for b in boards]


@router.delete("/{board_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_board(
    admin_user: AdminUser,  # 门禁升级：声明即触发 require_admin——member 在函数体执行前就被 403 挡住
    board_id: int,
    session: SessionDep,
) -> None:
    """删板：仅 admin。401（没登录）→ 403（登录了但不是 admin）→ 404（板不存在）→ 204。"""
    board = session.get(Board, board_id)  # 按主键取单条（04.1 的 get），比 select+where 短
    if board is None:
        raise HTTPException(status_code=404, detail="看板不存在")

    session.delete(board)  # 老三样的删除变体：delete → commit（没有 refresh——对象即将不在了）
    session.commit()
    # 不写 return：-> None 注解 + 204 = 响应体严格为空（测试断言 resp.content == b""）。
    # 进阶（docstring 提示的设计题）：板下的 task 行此刻成为孤儿行——SQLite 默认不强制外键，
    # 真项目会在迁移里给 task.board_id 加 ondelete="CASCADE"（models.py 进阶注释写过）。
    # 验收测试不考，但「删板连带什么」值得想清楚。

