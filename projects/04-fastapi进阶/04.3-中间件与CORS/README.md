# 04.3 中间件与 CORS

> 中间件是包住整个应用的「洋葱层」：请求进来先穿过它，响应出去再穿回来——计时、日志、CORS 都挂这一层。
> CORS 是前后端联调（模块 05）必遇的第一道坎：浏览器替用户拦下「别的源的响应」，服务器要用响应头表明「我允许」。

## 知识点速查

### 1. 中间件：`@app.middleware("http")`

```python
@app.middleware("http")
async def timing(request: Request, call_next):
    start = time.perf_counter()
    response = await call_next(request)          # 放行：进入里层，等里层产出响应
    response.headers["X-Process-Time-ms"] = "…"  # 收尾：响应后逻辑
    return response
```

- 必须是 `async def`：要 `await` 里层的结果（02.5 事件循环）。
- **洋葱模型**：多个中间件一层包一层；`add_middleware` **后注册的包在最外层**。请求从最外层穿到最里层，返回时逆序穿出——最外层最先进入、最后收尾。
- 404、HTTPException 的 JSON、/docs 页面也照样穿过中间件：它是**应用级**的。对比 03.5 的 yield 依赖——只包住「声明了它的端点」。

### 2. `call_next(request)`：放行

把请求交给洋葱里层并等待其结果。`call_next` **之前**是请求前逻辑，**之后**是响应后逻辑——
和 yield 依赖的前后半段神似，但包裹范围不同（见进阶提示分工表）；中间件自己抛的异常见易错点。

### 3. 同源的定义

协议 + 域名 + 端口，**任一不同即跨域**：

- `localhost:3000` → `127.0.0.1:3000`：域名不同（localhost ≠ 127.0.0.1），跨域！
- `localhost:3000` → `localhost:8000`：端口不同，跨域。同源请求则完全不走 CORS 检查。

### 4. 简单请求 vs 预检（OPTIONS）

- **简单请求**：GET/HEAD/POST 且只用常见头（`Content-Type` 限表单/纯文本那几种）→ 浏览器直接发真请求。
  拿到响应后检查 `Access-Control-Allow-Origin`，没有就拒收——Network 里能看到 200，但 JS 读不到。
- **非简单请求**（自定义头、PUT/DELETE、`Content-Type: application/json` 等）→
  浏览器**先偷偷发一个 OPTIONS 预检**问服务器「让不让」，通过了才发真请求；预检被拒则真请求根本不发。

### 5. CORSMiddleware 关键参数

| 参数 | 作用 | 默认 |
| --- | --- | --- |
| `allow_origins` | 允许的源白名单 | `[]` |
| `allow_origin_regex` | 用正则匹配源（如 `http://localhost:\d+`） | `None` |
| `allow_methods` | 允许的 HTTP 方法 | `["GET"]` |
| `allow_headers` | 允许的自定义请求头（预检会查） | `[]` |
| `allow_credentials` | 允许携带 Cookie 等凭证 | `False` |
| `expose_headers` | 允许前端 JS 读的额外响应头 | `[]` |

## 易错点

- `allow_origins=["*"]` 与 `allow_credentials=True` **互斥**（浏览器规范禁止）。
  starlette 不报错，而是把 `*` 悄悄换成「回显请求的 Origin」——等于全放行还带 Cookie，防护失效。
- 中间件里新建 `Response` 直接 return（短路）是张白纸：里层加过的响应头不会自动继承，该带的要自己带上。
  改响应体更麻烦（响应是流式写出的），能在依赖/路由里做的别挪进中间件。
- 忘加 CORSMiddleware 的报错长相：控制台 `has been blocked by CORS policy` 字样。
  接口其实返回了 200——拦你的是浏览器，不是服务器。
- 中间件自己抛异常 → 500 纯文本，**不走** 03.6 的异常处理器 JSON：异常处理器在洋葱更内层，只管路由里抛的。

## 进阶提示

| 机制 | 包裹范围 | 典型用途 |
| --- | --- | --- |
| 中间件 | 整个应用（含 404、/docs） | 计时、日志、CORS、GZip 压缩 |
| yield 依赖（03.5） | 声明了它的端点 | 开关数据库连接（04.1） |
| 异常处理器（03.6） | 路由内抛出的已注册异常 | 把异常翻译成统一 JSON |

- 验证「CORS 只是浏览器的规矩」：
  `curl -i -H "Origin: http://evil.com" .../books` → 照样 200，只是响应里没有 allow-origin 头。
- GZipMiddleware、SessionMiddleware 等官方中间件都用同一个 `add_middleware` 注册。

## 学习顺序与练习

1. 启动 `uv run fastapi dev "04.3-中间件与CORS/03-中间件.py"`，调 `/books`：
   F12 看响应头 `X-Process-Time-ms`，终端看 `[中间件]` 一行。
2. 访问 `/books/999` 和随便一个不存在的路径：404 也照样穿过中间件——这正是它和 yield 依赖的包裹范围差别。
3. 双击打开同目录 `cors-test.html`（file:// 页面的 Origin 是 `null`，不在白名单，正好观察被拦长相）：
   按钮 1 → F12 Console 出现 `blocked by CORS policy`；按钮 2 → Network 里先出现一条 OPTIONS 预检（400）。
4. 想看放行成功：把 `"null"` 临时加进 `allow_origins` 刷新再点（对照步骤 3 报错消失）。
   若浏览器连请求都没发出（Network 无记录），用 `python -m http.server 5500` 把页面挂在 http 源下再试。
5. 完成 TODO 1（日志中间件）、TODO 2（X-Request-ID）、TODO 3（思考题）。
