# 03.1 快速开始

> FastAPI 把「函数签名上的类型注解」翻译成三样东西：**校验规则、接口文档、JSON 序列化**。你在 02.4 手写的每个注解，从这里开始自动干活——这就是它和 Flask 最本质的差别。

## 知识点速查

### 1. FastAPI 是什么

名字里的 Fast 一语双关：**开发快**（注解即校验、文档白送）+ **性能快**（异步底座）。

两块地基，各管一层：

| 地基 | 管什么 |
|------|--------|
| Starlette | Web 层：路由、请求/响应对象、中间件 |
| Pydantic | 数据层：校验、序列化、schema 生成 |

服务器用 **uvicorn**（ASGI 服务器）：它才是真正监听端口、跑事件循环的程序；FastAPI 只是你 import 进来的一个库。

### 2. 安装（本项目已装好）

```bash
uv add "fastapi[standard]"
```

`[standard]` 是官方推荐的全家桶 extras：带上 uvicorn 服务器和 `fastapi` 命令行工具。不装 extras 就只有核心库，服务器要自己配——读别人项目的 pyproject 时认识这个写法即可（extras 语法在 02.6 提过）。

### 3. 第一个 API：三个角色

```python
from fastapi import FastAPI

app = FastAPI()        # ① 应用实例：所有路由都挂在它身上

@app.get("/")          # ② 路径操作装饰器：HTTP 方法 + 路径
def root() -> dict:    # ③ 路径操作函数：这次请求怎么处理
    return {"message": "你好"}   # 返回 dict → 自动序列化成 JSON 响应
```

记住这个固定结构：**装饰器定「在哪」，函数定「干什么」，返回值就是「响应体」**。

### 4. 运行：不是 python xxx.py

```bash
uv run fastapi dev "03.1-快速开始/01-快速开始.py"
```

- `fastapi dev`：开发模式，**改代码自动重载**，默认 <http://127.0.0.1:8000>；
- 直接 `python xxx.py` 只会「定义 app」然后退出——app 不会自己监听端口，起服务是 uvicorn 的活；
- 生产部署用 `fastapi run`（不讲 dev 的热重载），到模块 04 部署章再细说。

### 5. 自动文档：白送的

| 地址 | 是什么 |
|------|--------|
| `/docs` | Swagger UI：全部接口可视化，能直接 Try it out 发请求 |
| `/redoc` | ReDoc：同一份信息的另一种排版，适合阅读 |
| `/openapi.json` | 上面两个页面的数据源——FastAPI 从你的**注解 + docstring**自动生成的接口描述 |

文档不是魔法：你给路径操作函数写的参数注解、返回注解、docstring，全部会出现在 `/docs` 里。**文档 = 注解的影子**。

### 6. 返回值不挑食

`dict` / `list` / `str` / `int` 都能直接返回（自动 JSON 化）；Pydantic 模型也能返回（03.3 起）；需要精确控制响应头/状态码时用 `Response`（03.4）。

## 易错点

- `python 01-快速开始.py` 没反应——它只定义了 app，起服务要用 `fastapi dev`。
- 改了代码没生效——确认 `fastapi dev` 还开着（它才自动重载）；自己用 uvicorn 裸跑要手动加 `--reload`。
- POST/PUT 在浏览器地址栏测不了（地址栏只会发 GET）——用 `/docs` 的 Try it out。
- 装饰器路径漏了开头的 `/`：`@app.get("items")` 直接报错，必须 `"/items"`。
- `async def` 路由里写了 `time.sleep(3)` 会**卡住整个服务**（阻塞事件循环，02.5 的坑在服务端复现）——要么用 `await asyncio.sleep()`，要么把函数写成普通 `def`（FastAPI 会自动把它丢进线程池，不卡别人）。

## 进阶提示

- 端口被占用：`fastapi dev --port 8001`。
- 路径操作函数的 docstring 支持 Markdown，会渲染进 `/docs`——接口怎么用直接写在 docstring 里，文档即代码。
- FastAPI 默认对同一路径**先注册的先匹配**，写路由时把更具体的路径放前面（03.2 会遇到经典案例 `/me` vs `/{user_id}`）。

## 学习顺序与练习

先 `fastapi dev` 启动，浏览器访问 `/` 和 `/items`，再打开 `/docs` 对照着看代码；然后完成 TODO，每写完一个路由保存一次，观察自动重载和文档变化。

TODO（见 `01-快速开始.py`）：
1. 写 `GET /ping`，返回 `{"pong": True}`——最小闭环练习。
2. 写 `GET /about`，返回介绍自己的 dict，并到 `/docs` 确认 docstring 出现了。
3. 观察题：对比 `/docs` 和 `/redoc`，一句话写下区别。
