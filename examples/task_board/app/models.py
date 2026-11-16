"""M1 · 表模型——你的第一块拼图（04.1：一个类身兼两职）

全部 5 张表的字段规格见 README「数据模型」节。写法提示：
- 表模型加 table=True，id 都是 `int | None = Field(default=None, primary_key=True)`；
- 外键用 Field(foreign_key="表名.id")（如 foreign_key="user.id"，表名 = 类名小写）；
- assignee_id 可空：`int | None = Field(default=None, foreign_key=...)`——「还没分配」是正常状态；
- 请求/响应模型不写在这里（去 schemas.py）——主键轮不到客户端定（03.4 白名单思想）。

⚠️ 本文件完成前，验收测试会以「no such table」的方式变红——这就是 TDD 的红。
"""

from datetime import datetime

from sqlalchemy import ForeignKey, Integer
from sqlmodel import DateTime, SQLModel, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.orm import DeclarativeBase


class Base(DeclarativeBase):
    """所有 ORM 模型的父类，用于集中保存表结构的 MetaData。"""


# TODO M1：依次定义 5 个表模型——User / Board / Task / Notification / Activity
class User(Base):
    """用户表"""

    __tablename__ = "users"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    username: Mapped[str] = mapped_column(String(50), unique=True, nullable=False)
    hashed_password: Mapped[str] = mapped_column(String(255), nullable=False)


class Board(Base):
    """看板表"""

    __tablename__ = "board"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    title: Mapped[str] = mapped_column(String(50), unique=True, nullable=False)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
    )


class Task(Base):
    """任务表"""

    __tablename__ = "tasks"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    title: Mapped[str] = mapped_column(String(50), unique=True, nullable=False)
    content: Mapped[str] = mapped_column(Text, nullable=False)
    board_id: Mapped[int] = mapped_column(
        ForeignKey("board.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
    )


class Notification(Base):
    """通知消息表"""

    __tablename__ = "notification"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    title: Mapped[str] = mapped_column(
        ForeignKey("tasks.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
