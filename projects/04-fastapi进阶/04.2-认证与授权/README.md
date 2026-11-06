# 04.2 认证与授权

> 认证（authentication）回答「你是谁」，授权（authorization）回答「你能干什么」。这一章把 03.5 的假
> token 换成真家伙：密码用 bcrypt 哈希、身份用 JWT 签名，再靠依赖链保护路由——03.5 的铺垫全部兑现。

## 知识点速查

### 1. 哈希 vs 加密：一字之差，用途完全不同
- **加密是双向的**：有密钥能解开，适合传输数据；**哈希是单向的**：不可逆，只能「验对不对」，适合存密码。
- 数据库泄露时，攻击者拿到的只是「指纹」，登不进任何账号。
- bcrypt 每次加**随机盐**（gensalt）：同一密码两次哈希结果都不同，彩虹表（预计算指纹库）失效。

```python
hashed = bcrypt.hashpw("admin123".encode(), bcrypt.gensalt()).decode()  # 注册时：存它
bcrypt.checkpw("admin123".encode(), hashed.encode())                    # 登录时：验它
```

### 2. JWT：三段 base64url，用 `.` 连接
`header.payload.signature`：
- **header**：`{"alg": "HS256", "typ": "JWT"}`——声明用什么算法签的。
- **payload**：`{"sub": "zhang", "exp": 1730000000}`——谁、活到几点。**只是 base64 不是加密，人人能解开看**，
  所以里面只放用户名和过期时间。
- **signature**：用只有服务器知道的 `SECRET_KEY` 对前两段算出的签名。

### 3. 签名为什么防篡改
校验时服务器对收到的 header.payload **重算一遍签名**，与第三段比对：改一个字节（哪怕把 sub 改成别人），
重算结果就对不上 → 401。base64 只负责「编码」，签名才负责「保真」——所以 `SECRET_KEY` 绝不能泄露。

```python
token = jwt.encode({"sub": "zhang", "exp": ...}, SECRET_KEY, algorithm="HS256")   # 签发
payload = jwt.decode(token, SECRET_KEY, algorithms=["HS256"])  # 校验：验签名 + 验 exp 一步完成
```

### 4. OAuth2PasswordBearer 与 /docs 的 Authorize 按钮
`OAuth2PasswordBearer(tokenUrl="login")` 干两件事：
1. 对每个请求：从请求头 `Authorization: Bearer xxx` 抠出 token（03.4 Header 的自动化版），没带就 401。
2. 对 /docs：声明「token 去 POST /login 换」——于是右上角出现 **Authorize 按钮**。

**Authorize 怎么用**：点它 → 弹窗里输 username / password → 它实际是向 /login 发了一个表单
（OAuth2 规定登录接口收表单，所以这里首次见到 `OAuth2PasswordRequestForm`）→ 拿到 token 后
/docs 自动把它填进后续每个请求的头里。接口旁的 🔒 图标 = 这个接口要登录。

### 5. get_current_user 依赖链（03.5 链条的真实版）

```text
oauth2_scheme 抠token → jwt.decode 验签名/过期 → 查内存库取用户 → return user → require_admin 再查角色
```

每层一个普通函数、可单独测试（02.7 pytest），路由只声明 `Depends(get_current_user)`；
`require_admin` 叠在它之上，非 admin 抛 403（03.6）。

## 易错点
- **SECRET_KEY 硬编码进代码**：提交到 git = 任何人都能伪造合法 token。真实项目用环境变量 / 配置文件
  （`os.environ["SECRET_KEY"]`），别写死。
- **jwt.decode 不验算法 / 签发不放 exp**：`algorithms=["HS256"]` 必须显式传（否则攻击者可换弱算法伪造）；
  payload 不带 `exp` 的 token 永不过期，泄露后无法自愈。
- **把密码塞进 token payload**：payload 只是 base64 不是加密，粘到解码网站人人可读。token 里只放
  `sub` 和 `exp`。
- **checkpw 的 bytes/str 坑**：bcrypt 全程用 bytes——`checkpw(明文.encode(), 存的哈希.encode())`，
  漏 encode 直接 TypeError；入库时 `.decode()` 转回 str 只是为了适配数据库的字符串列。

## 进阶提示
- token payload 里故意不放 role：权限每次从数据库现查——token 是「签发时刻的快照」，刚升管理员不用重登。
- 下一步自然延伸：短期 access_token + 长期 refresh_token 换发、`jti` 黑名单实现「主动踢下线」。

## 学习顺序与练习

启动 `uv run fastapi dev "04.2-认证与授权/02-认证.py"`，按这个顺序玩 /docs：

1. POST /hash-demo：同一密码哈希两次，看两个哈希是否不同、checkpw 是否都认对的那个。
2. POST /register 注册自己 → POST /login 拿 token（或直接用右上角 Authorize 登录，两种等价）。
3. 带 token 访问 GET /me → 换 li（reader）访问 GET /admin/books 看 403 → 再用 zhang（admin）看 200。
4. 完成 TODO：① 给 DELETE /books/{book_id} 加管理员保护 ② 把 ACCESS_TOKEN_EXPIRE 改成 1 秒，
   睡 2 秒访问 /me 看过期 401 ③ 篡改 token 第三段，看签名校验 401。
