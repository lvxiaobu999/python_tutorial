# 04.6 测试与部署

> 之前验证接口靠 `fastapi dev` 手点 /docs，这一章让**机器替你点**：pytest + TestClient 把请求直接打进 app、逐条断言响应码；测稳了再用 Docker 把「代码 + 依赖 + 启动命令」打成一个随处可跑的镜像。没装 Docker 就先只做 pytest 部分——测试才是本章核心。

## 知识点速查

### 1. TestClient：不起服务器，进程内直调 ASGI app

```python
from fastapi.testclient import TestClient
client = TestClient(app)        # app 就是 06-测试与部署.py 里的 FastAPI 实例
resp = client.get("/books/1")   # 请求不经过网络、不占端口，毫秒级返回
assert resp.status_code == 404  # 精确拿到状态码/JSON，断言不靠肉眼
```

原理：FastAPI 的 `app` 本身就是一个 ASGI 应用（uvicorn 干的活就是调它）。
TestClient 在进程内直接调用 app，省掉「起服务器」这一步——所以测试快，且能精确断言。

### 2. pytest fixture：测试的「准备工序」（02.7 兑现）
测试函数声明 `client` 参数 → pytest 自动调 fixture，造好客户端、重置完数据再递进来。
每个测试拿到的都是干净状态：准备与验证分离，测试之间谁也不欠谁。

### 3. 测试到底在断言哪些响应码

| 码 | 含义 | 对应章节 |
|----|------|---------|
| 200 | 查询成功 | 03.1/03.2 路由 |
| 201 | 创建成功 | 03.4 状态码 |
| 204 | 成功且无响应体 | 03.4（DELETE 搭档） |
| 404 | 资源不存在 | 03.6 HTTPException |
| 422 | 请求体校验失败 | 03.3 Pydantic |
| 401 | 未登录（本章暂不测，04.2 学完回补） | 04.2 认证 |

### 4. uvicorn 与 gunicorn 的分工
- uvicorn：ASGI 服务器，真正干活，但默认单进程。
- gunicorn：进程管理器（多 worker、崩了自动拉起），但只支持 WSGI，且不支持 Windows。
- Linux 生产的常见组合：`gunicorn -k uvicorn.workers.UvicornWorker app:app`——gunicorn 管进程，uvicorn 当 worker。

### 5. Docker 镜像层缓存
Dockerfile 每条指令生成一层，输入没变就直接复用缓存。所以把「装依赖」（很少变）
放在「COPY 代码」（天天变）之前：改代码重建时依赖层秒过，不用重新下载安装。

### 6. build / run 两条命令

```bash
# 在 projects/04-fastapi进阶 目录下（-f 指定 Dockerfile，. 是构建上下文，须含 pyproject.toml）
docker build -f "04.6-测试与部署/Dockerfile" -t books-api .
# 标准形态：Dockerfile 与 pyproject.toml 同在项目根时，就是 docker build -t books-api .
docker run --rm -p 8000:8000 books-api   # -p 宿主端口:容器端口，之后开 127.0.0.1:8000/docs
```

Windows 要先装 Docker Desktop 才有 docker 命令；没装就先只做 pytest 部分（测试才是本章核心）。

## 易错点
- **测试间状态污染**：books 是模块级 dict，活得比测试久，上一个测试插的书残留给下一个 → 测试结果依赖执行顺序。fixture 里每个测试前 `reset_books()`，保证任何顺序都绿。
- **TestClient 默认把 500 变异常**：`raise_server_exceptions=True`（默认）时，服务端异常直接在测试里抛出而不是返回 500；想「真收 500 再断言」，用 `TestClient(app, raise_server_exceptions=False)`。
- **`COPY . .` 把 .venv 也拷进镜像**：几百 MB 的 Windows 虚拟环境塞进 Linux 容器，跑不了还巨肥——在构建上下文根放 `.dockerignore`（本项目已放：.venv、__pycache__、*.db、*.md）。
- **容器里监听 127.0.0.1 连不上**：127.0.0.1 只收「容器自己发给自己」的连接，`-p` 映射进来的流量算外部 → 必须监听 `0.0.0.0`。

## 进阶提示
- `app.dependency_overrides[get_session] = ...`：不改业务代码替换掉 Depends 依赖——测 04.1 数据库版接口的钥匙（见 test_06.py 尾部 TODO 1）。
- TDD 循环：先写一条必失败的测试（红）→ 写实现让它通过（绿）——TODO 2 带你完整走一遍。
- 本章这套测试不加改动就能进 CI：`uv run pytest` 全绿即放行合并。

## 学习顺序与练习

本章不跑 `fastapi dev`，在 `projects/04-fastapi进阶` 目录下跑测试：

```bash
uv run pytest "04.6-测试与部署/test_06.py" -v    # 全绿即通过；等价命令见 test_06.py 文件头
```

1. 先读 `06-测试与部署.py`：故意保持简单的 CRUD，重点想「它将如何被测」。
2. 逐条读 `test_06.py`：注释标了每条测试对应 03 的哪一章；故意改坏一个断言，看 pytest 怎么报错。
3. TODO 1：给 04.1 数据库版接口写测试，用 `dependency_overrides` 覆盖 `get_session`。
4. TODO 2：写一条必红的测试再修绿，体验 TDD。
5. 装了 Docker Desktop 再做部署部分：build → run → 开 127.0.0.1:8000/docs。
