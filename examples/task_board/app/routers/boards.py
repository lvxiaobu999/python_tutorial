"""M3 · 看板路由——任务的「房间」划分（也划定了 M6 广播的范围）

端点规格：
- POST /boards          201 → {"id", "name"}；需登录（401）
- GET /boards           200 → [{"id", "name"}...]；需登录
- DELETE /boards/{id}   204；⭐ 仅 admin（403）——require_admin 的第一个自然落点（04.2 TODO1 同款）
                        板不存在 → 404；删除成功响应体必须为空（204 的语义，03.4）

写法提示：
- 删板时要不要连带删任务？验收测试不考——想清楚即可（真项目叫级联删除，README 加分项提了）。
"""

from fastapi import APIRouter, status

from app.database import SessionDep
from app.deps import CurrentUser
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
