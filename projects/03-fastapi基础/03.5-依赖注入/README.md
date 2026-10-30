# 03.5 依赖注入

> `Depends` 是 FastAPI 最独特的特性：把「多个接口共用的逻辑」抽成普通函数，在参数里声明「我需要它」，框架负责调用、传参、组装。学完它，分页参数、登录校验都只写一遍。

## 知识点速查

### 1. Depends：把函数变成「插头」

```python
def pagination(skip: int = 0, limit: int = 10) -> dict:
    return {"skip": skip, "limit": limit}

@app.get("/books")
def list_books(page: Annotated[dict, Depends(pagination)]) -> dict: ...
```

- `pagination` 的参数自动成为 /books 的**查询参数**（不用在路由里再写一遍）。
- 返回值作为 `page` 传进路由函数。
- `Annotated[类型, Depends(函数)]`：FastAPI 的现代写法。

### 2. 复用：声明多少次，就复用多少次
同一个依赖被 5 个接口用 → 分页逻辑只有 1 份。改默认值、加参数只动依赖函数一处。

### 3. 依赖链
依赖的参数里还能 `Depends(别的依赖)`：token 校验 → 取当前用户 → 判断权限，层层组装，每层都是独立函数、可单独测试（02.7 的 pytest 正好用上）。

### 4. yield 依赖：前逻辑 + 后逻辑

```python
def fake_db():
    conn = open_conn()   # 请求前：取连接
    yield conn           # 交给路由函数用
    conn.close()         # 响应后：归还
```

`yield` 前是 setup、后是 teardown（02.3 生成器的老朋友）——数据库会话的标准形态。

### 5. 全局 / 组级依赖（知道即可）
`FastAPI(dependencies=[...])` 和 router 的 `dependencies` 参数：给一批路由统一加检查。

## 易错点
- `page: dict = Depends(pagination)`（不带 Annotated）也能跑，但风格统一用 Annotated，两种混写难读。
- 依赖函数的参数没默认值 → 变成**必填**查询参数，客户端不传就 422。
- 别把「请求状态」存成模块级全局变量——每个请求都会执行依赖，会互相踩。
- yield 依赖的 teardown 在响应之后执行：别在里面改响应内容（改响应用 03.4 的 Response 参数）。

## 进阶提示
- 类也能当依赖：`__init__` 的参数就是依赖的参数（04.2 认证章的常用形态）。
- 依赖有缓存：同一次请求内，同一个依赖只执行一次，多处声明不重复计算；`Depends(x, use_cache=False)` 可关掉。

## 学习顺序与练习

启动 `uv run fastapi dev "03.5-依赖注入/05-依赖注入.py"`，对照 /docs 观察依赖参数如何变成查询参数，再完成 TODO：

1. TODO 1：写排序依赖 `sort_options`（`sort_by` 查询参数，默认 `"title"`），与分页依赖同用。
2. TODO 2：把分页依赖用到大作业的图书列表接口 `/library/books`。
3. TODO 3：依赖链——给分页再包一层 `valid_page`，强制 `limit ≤ 50`。
