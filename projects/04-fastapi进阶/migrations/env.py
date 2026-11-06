from logging.config import fileConfig
from pathlib import Path

from sqlalchemy import engine_from_config
from sqlalchemy import pool

from alembic import context

# this is the Alembic Config object, which provides
# access to the values within the .ini file in use.
config = context.config

# 连接串不写进 alembic.ini：ini 按 Windows 本地编码（GBK）读取，项目路径里的中文
# 会让它 UnicodeDecodeError。这里是 Python 源码、永远按 UTF-8 读，中文路径无压力。
# 「相对本文件定位」的老套路（01-数据库.py 的 DB_PATH 同款）——迁移和 App
# 操作同一个 books.db；三个斜杠 + 正斜杠路径是 sqlite URL 的标准写法。
DB_PATH = Path(__file__).resolve().parents[1] / "04.1-数据库集成" / "books.db"
config.set_main_option("sqlalchemy.url", f"sqlite:///{DB_PATH.as_posix()}")

# Interpret the config file for Python logging.
# This line sets up loggers basically.
if config.config_file_name is not None:
    fileConfig(config.config_file_name)

# add your model's MetaData object here
# for 'autogenerate' support
# autogenerate 的原理是对比「模型定义 vs 数据库现状」，所以必须先把模型加载进来。
# 模型在 04.1-数据库集成/01-数据库.py——非包结构 + 中文路径，用 importlib 按路径加载；
# 加载会执行模块级代码（建 engine、create_all），都是幂等操作，无副作用。
import importlib.util

_models_path = Path(__file__).resolve().parents[1] / "04.1-数据库集成" / "01-数据库.py"
_spec = importlib.util.spec_from_file_location("app_models_04_1", _models_path)
_models = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(_models)
target_metadata = _models.SQLModel.metadata

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
    url = config.get_main_option("sqlalchemy.url")
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
        context.configure(
            connection=connection, target_metadata=target_metadata
        )

        with context.begin_transaction():
            context.run_migrations()


if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()
