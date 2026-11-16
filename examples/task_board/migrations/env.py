from logging.config import fileConfig
import sys
from pathlib import Path

from sqlalchemy import engine_from_config
from sqlalchemy import pool

from alembic import context

# this is the Alembic Config object, which provides
# access to the values within the .ini file in use.
config = context.config

# 连接串不写进 alembic.ini：ini 按 Windows 本地编码（GBK）读取，中文路径/注释会让它
# UnicodeDecodeError；env.py 是 Python 源码、永远按 UTF-8 读，无压力（projects/04 同款）。
# DB_PATH 直接复用 app.database 的定义——App 和迁移操作同一个库，单一事实来源。
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))  # 项目根（app/ 的上级）
from app.database import DB_PATH  # noqa: E402

config.set_main_option("sqlalchemy.url", f"sqlite:///{DB_PATH.as_posix()}")

# Interpret the config file for Python logging.
# This line sets up loggers basically.
if config.config_file_name is not None:
    fileConfig(config.config_file_name)

# add your model's MetaData object here
# for 'autogenerate' support
# autogenerate 的原理 = 对比「模型定义 vs 数据库现状」，所以必须先把模型加载进来
# （导入即注册进 SQLModel.metadata），否则 target_metadata=None → 生成的迁移是空的。
from app import models  # noqa: F401,E402

# 经 models 模块属性访问（而非裸名 SQLModel）——与 projects/04 的 env.py 同款，
# 顺便规避 Pylance 对 SQLModel 元类的一族静态误报
target_metadata = models.SQLModel.metadata

# other values from the config, defined by the needs of env.py,
# can be acquired:
# my_important_option = config.get_main_option("my_important_option")
# ... etc.


def run_migrations_offline() -> None:
    """Run migrations in 'offline' mode.

    This configures the context with just a URL
    and not an Engine, though an Engine is acceptable
    here as well.  By skipping the Engine creation
    we don't even need a DBAPI to be available.

    Calls to context.execute() here emit the given string to the
    script output.

    """

    DB_PATH = Path(__file__).resolve().parent.parent / "task_board.db"

    url = config.get_main_option(
        "sqlalchemy.url",
        f"sqlite:///{DB_PATH}",
    )
    context.configure(
        url=url,
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
    )

    with context.begin_transaction():
        context.run_migrations()


def run_migrations_online() -> None:
    """Run migrations in 'online' mode.

    In this scenario we need to create an Engine
    and associate a connection with the context.

    """
    connectable = engine_from_config(
        config.get_section(config.config_ini_section, {}),
        prefix="sqlalchemy.",
        poolclass=pool.NullPool,
    )

    with connectable.connect() as connection:
        context.configure(connection=connection, target_metadata=target_metadata)

        with context.begin_transaction():
            context.run_migrations()


if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()
