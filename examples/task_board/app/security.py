"""M2 · 密码哈希 + JWT——04.2 的核心逻辑搬进独立模块

工程形态的新排布：04.2 全写在一个文件里；现在按职责拆——
本文件只管「密码怎么存、token 怎么签/验」，「谁能进来」的判断在 deps.py。

四个函数的规格（实现思路 04.2 都写过，别抄作业——先回忆再对照）：
- hash_password(plain) -> str：bcrypt.hashpw + gensalt（随机盐让同一密码两次哈希不同）
- verify_password(plain, hashed) -> bool：bcrypt.checkpw——「验」不靠还原
- create_token(username) -> str：payload 只放 sub + exp（config.py 里有现成常量）
- decode_token(token) -> str：验签 + 验过期，成功返回 sub（用户名）；
  任何无效（jwt.InvalidTokenError）向上抛，让调用方决定怎么拒绝
"""

# TODO M2：实现上面 4 个函数
