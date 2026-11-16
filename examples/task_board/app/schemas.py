"""M2/M3 · 请求与响应模型——和表模型分开的「门口模型」（03.3 / 03.4）

需要的模型（字段规格见 README「API 规格」节）：
- RegisterIn：username / password（POST /register 的请求体）
- UserPublic：id / username / role——注意：**绝不含 password_hash**（03.4 响应模型白名单）
- TaskCreate / TaskUpdate / TaskPublic
- status 字段用 Literal["todo", "doing", "done"] 限定（03.5 笔记踩过：别写 "todo" | "doing" 联合类型，
  静态检查器认、运行时 TypeError）

写法提示：
- TaskUpdate 所有字段都可省（PATCH 语义：只改带来的字段）——配合 exclude_unset 使用；
- TaskPublic 不含任何内部字段，响应长什么样由它的字段清单说了算。
"""

# TODO M2：RegisterIn / UserPublic；TODO M3：TaskCreate / TaskUpdate / TaskPublic
