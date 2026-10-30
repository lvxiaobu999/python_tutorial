# 03.4 响应模型

> 03.3 管「进来的数据」，这一章管「出去的数据」：`response_model` 决定响应长什么样（多余字段不放行），`status_code` 给成功标语义，Header/Cookie 是 HTTP 协议里的「请求随身信息」。

## 知识点速查

### 1. response_model：响应的白名单

```python
@app.get("/users/{name}", response_model=UserOut)
def get_user(name: str) -> dict:
    return {"username": name, "email": "...", "password": "绝密"}
```

- 函数返回值里带 `password`，但响应里**只有 UserOut 声明的字段**——多出来的被过滤。
- 和 03.3 对偶：请求模型管入口，响应模型管出口。
- /docs 也按 UserOut 展示响应结构——前端照着写类型。

### 2. status_code：给成功标语义

| 写法 | 场景 |
|------|------|
| `200`（默认） | 查询 |
| `status.HTTP_201_CREATED` | 创建成功 |
| `status.HTTP_204_NO_CONTENT` | 删除成功（无响应体） |

写在装饰器上 `status_code=201`，文档同步显示预期状态码。

### 3. 读请求头 / Cookie：Annotated + Header() / Cookie()

```python
user_agent: Annotated[str | None, Header()] = None
session_id: Annotated[str | None, Cookie()] = None
```

- `Header()` 自动把 `user_agent` 映射成 HTTP 头 `User-Agent`（下划线 ↔ 连字符）。
- `Annotated[类型, 附加信息]` 是 FastAPI 的推荐写法——02.4 的 typing 在框架里的实战延续。

### 4. 写 Cookie / 响应头：声明 `response: Response`

```python
def login(response: Response):
    response.set_cookie(key="session_id", value="abc123")
```

不影响正常 return——返回值照常，额外信息挂在 response 上。

## 易错点
- 响应模型声明了字段但返回值里没有 → 响应缺字段（不报错，但前端拿不到）。
- `204` 还想返回数据 → 204 的定义就是无 body；要带数据用 200/201。
- 参数名只能用下划线（`user_agent`），连字符版本靠 `Header()` 自动映射，别写 `user-agent`。
- Cookie 看不到？先访问 /login 种 Cookie；/docs 的请求从浏览器发出才带得上 Cookie。

## 进阶提示
- `response_model_exclude_unset=True`：只回显显式设置的字段（PATCH 部分更新常用）——这正是 03.3 说的「没传」和「传 null」的区别兑现的地方。
- 响应头也能自定义：`response.headers["X-Total-Count"] = "42"`，分页总数的常见放法。
- `response_class=RedirectResponse` 可把接口变成重定向。

## 学习顺序与练习

启动 `uv run fastapi dev "03.4-响应模型/04-响应模型.py"`，对照 /docs 和浏览器 DevTools 玩演示，再完成 TODO：

1. TODO 1：`BookOut` 白名单——把带进价（内部字段）的图书数据滤干净。
2. TODO 2：创建图书返回 201，观察文档里预期状态码的变化。
3. TODO 3：Cookie 闭环 `/login` → `/whoami`，并在 DevTools → Application → Cookies 里亲眼看到它。
