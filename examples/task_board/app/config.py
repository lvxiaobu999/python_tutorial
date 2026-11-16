"""配置：真实项目的密钥不该写死进代码（04.2 的教训）。

SECRET_KEY 优先从环境变量读；没有时用开发兜底值——
练习可以兜底，提交到 git 的生产代码必须只从环境变量拿。
"""

import os

SECRET_KEY = os.environ.get("TASKBOARD_SECRET", "dev-only-secret-change-me-32bytes!")
ALGORITHM = "HS256"  # 对称签名：签发与校验同一把密钥（04.2）
ACCESS_TOKEN_EXPIRE_SECONDS = 30 * 60  # 30 分钟
