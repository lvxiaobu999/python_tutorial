# 03.2 路由

> 路由回答「什么请求交给哪个函数」。URL 里能装的信息有三处——**路径、查询串、请求体**，加上拆分大项目的 APIRouter，就是这一章的全部。02.4 的类型注解从这一章开始真正「干活」。

## 知识点速查

### 1. 路径参数：URL 里定位资源
- `@app.get("/items/{item_id}")` + `def f(item_id: int)`：占位符与参数**同名**即可接住。
- 注解决定行为：`int` → 自动把 `"3"` 转成 `3`；传 `abc` → 422 校验错误。
- 注解 `str` → 原样接收字符串（不做转换）。

### 2. 路径顺序：先注册先匹配
| 写法 | 说明 |
|------|------|
| `/users/me` | 固定路径，必须写在通配路径**前面** |
| `/users/{user_id}` | 通配路径；写反了顺序，`me` 会被当成 `user_id` 吃掉 |

### 3. 查询参数：`?key=value`
不在路径占位符里的函数参数，自动变成查询参数：

| 函数签名 | 行为 |
|----------|------|
| `keyword: str` | **必填**，缺了报 422 |
| `keyword: str = "默认"` | 可选，有默认值 |
| `keyword: str \| None = None` | 可选，可为空 |
| `active: bool = True` | 自动转换：`?active=false` → `False`（还认 `"1"`/`"0"`/`"yes"`/`"no"`） |

### 4. 请求体：客户端提交的数据
- 参数类型是 **Pydantic BaseModel** 时，FastAPI 把请求体 JSON 校验后传进来（03.3 细讲）。
- POST/PUT/DELETE 用 `/docs` 的 Try it out 测——地址栏只会发 GET。

### 5. 组合使用
路径参数 + 查询参数 + 请求体可以同时出现，各归各位：
`@app.put("/users/{user_id}/items/{item_id}")` → `user_id`、`item_id` 走路径，其余命名参数走查询，模型参数走请求体。

### 6. APIRouter：路由多了怎么管
- `router = APIRouter(prefix="/shop", tags=["商店"])`：`prefix` 统一加前缀，`tags` 在 /docs 里分组。
- 路由挂在 `@router.get(...)` 上，最后 `app.include_router(router)` 挂回主应用。
- 大项目标准结构：一个业务模块一个 router，各自成文件。

## 易错点
- 占位符和参数名不一致：路径写 `{item_id}`，参数就得叫 `item_id`；写 `{id}` 就接不到。
- `/users/me` 注册在 `/users/{user_id}` 之后 → `me` 被当成 `user_id`。
- 路径漏开头的 `/`：`@app.get("items")` 直接报错，必须 `"/items"`。
- 用浏览器地址栏测 POST → 地址栏只会发 GET，去 /docs 用 Try it out。
- 查询参数 `keyword: str` 不给默认值 → 变成必填，不传就 422。

## 进阶提示
- 路径参数用枚举限定取值：`class Platform(str, Enum)`，文档里直接出下拉框。
- 吞多级路径：`/files/{file_path:path}`（`:path` 转换器），能匹配 `a/b/c.txt`。
- router 也有 `dependencies` 参数，可给整组路由统一加依赖（03.5 见）。

## 学习顺序与练习

先启动 `uv run fastapi dev "03.2-路由/02-路由.py"`，逐个玩演示接口（重点观察 /docs 里参数是怎么被识别的），再完成 TODO：

1. TODO 1：`GET /books/{book_id}`，感受 `int` 注解的自动转换与 422。
2. TODO 2：`GET /tasks`，可选 bool + 可选 str 的查询参数组合。
3. TODO 3：`POST /tasks`，最小请求体——期末大作业的雏形。
