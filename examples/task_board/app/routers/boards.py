"""M3 · 看板路由——任务的「房间」划分（也划定了 M6 广播的范围）

端点规格：
- POST /boards          201 → {"id", "name"}；需登录（401）
- GET /boards           200 → [{"id", "name"}...]；需登录
- DELETE /boards/{id}   204；⭐ 仅 admin（403）——require_admin 的第一个自然落点（04.2 TODO1 同款）
                        板不存在 → 404；删除成功响应体必须为空（204 的语义，03.4）

写法提示：
- 删板时要不要连带删任务？验收测试不考——想清楚即可（真项目叫级联删除，README 加分项提了）。
"""

from fastapi import APIRouter

router = APIRouter(tags=["boards"])
