# ==================================================================
# 04.6 部署：把图书 API 打包成 Docker 镜像
# 构建（在 projects/04-fastapi进阶 目录下，. 是「构建上下文」的根）：
#     docker build -f "04.6-测试与部署/Dockerfile" -t books-api .
# 运行：
#     docker run --rm -p 8000:8000 books-api
#     然后浏览器开 http://127.0.0.1:8000/docs
# ==================================================================

# ---- 第 1 步：基础镜像 python:3.13-slim ----
# slim = 砍掉编译工具链的精简 Debian：比完整版小几百 MB，纯跑 FastAPI 够用；
# 版本钉死 3.13，和 pyproject.toml 的 requires-python 对齐——本地、容器行为一致。
FROM python:3.13-slim

# ---- 第 2 步：装 uv（官方推荐做法：从 uv 官方镜像里直接拷二进制） ----
# 不走 pip install uv：直接拷可执行文件，镜像里不留 pip 安装的中间产物，又快又干净。
# （生产建议把 latest 换成固定版本号，让构建可复现；练习图方便先用 latest。）
COPY --from=ghcr.io/astral-sh/uv:latest /uv /uvx /bin/

# ---- 第 3 步：工作目录 /app——之后所有相对路径都以它为基准 ----
# 容器里不关心你从哪个目录启动，路径永远确定，出错好排查。
WORKDIR /app

# 日志不被 Python 缓冲困住：不加它，容器里 print 的输出会攒够一批才吐出来
ENV PYTHONUNBUFFERED=1

# ---- 第 4 步：先只 COPY 依赖清单，再装依赖——「层缓存」的胜负手 ----
# Dockerfile 每条指令生成一层；某层的输入没变，下次构建就直接复用缓存。
# 依赖清单很少改、源代码天天改：把「装依赖」放在「COPY 代码」之前，
# 改一行代码重建镜像时依赖层缓存命中，几秒完成，不必重新下载安装。
COPY pyproject.toml uv.lock ./
RUN uv sync --frozen --no-install-project
# --frozen           ：严格按 uv.lock 装——锁文件里是什么就装什么（可复现构建）
# --no-install-project：只装第三方依赖，不把练习项目本身构建成包（脚本式练习）

# ---- 第 5 步：再 COPY 代码（必须排在装依赖之后，理由见第 4 步） ----
# 顺手改名为 app.py：uvicorn 的启动参数是「模块名:变量名」的 import 字符串，
# 而「06-测试与部署」以数字开头、带连字符，写不成合法模块名——改名最省事。
# 测试文件不拷进镜像：镜像是用来跑服务的，不是用来跑 pytest 的。
COPY "04.6-测试与部署/06-测试与部署.py" ./app.py

# ---- 第 6 步：把虚拟环境的 bin 目录加进 PATH ----
# 依赖装在 /app/.venv，uvicorn 可执行文件在 /app/.venv/bin——
# 加进 PATH 后 CMD 才能直接写 uvicorn，不必每次都 uv run。
ENV PATH="/app/.venv/bin:$PATH"

# ---- 第 7 步：EXPOSE 8000——只是「声明」本服务打算用 8000 端口 ----
# 它不做任何映射（纯元数据/文档作用），真正的端口映射发生在 docker run -p。
EXPOSE 8000

# ---- 第 8 步：容器启动命令——uvicorn 监听 0.0.0.0:8000 ----
# 为什么必须是 0.0.0.0 而不是默认的 127.0.0.1：127.0.0.1 只接受「容器自己
# 发给自己」的连接；-p 映射进来的流量对容器来说是外部来的，监听 127.0.0.1
# 一律拒收——表现就是端口映射正常、宿主机却怎么都连不上。0.0.0.0 = 监听
# 所有网卡，外部流量才进得来。
# （多核服务器上生产常用 gunicorn 管理多个 uvicorn worker 进程，见 README 速查 4。）
CMD ["uvicorn", "app:app", "--host", "0.0.0.0", "--port", "8000"]
