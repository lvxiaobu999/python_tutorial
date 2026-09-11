# uv 使用指南

`uv` 是一个用 Rust 写的极快 Python 包与项目管理器，同时替代 `pip`、`virtualenv`、`pipx` 等工具。本项目全程用它管理依赖。

---

## 一、安装 uv

```bash
# Windows (PowerShell)
powershell -ExecutionPolicy ByPass -c "irm https://astral.sh/uv/install.ps1 | iex"

# macOS / Linux
curl -LsSf https://astral.sh/uv/install.sh | sh

# 验证
uv --version
```

> 也可以 `pip install uv` 安装，但推荐用官方脚本获得独立可执行文件。

---

## 二、开启一个新项目

### 1. 初始化项目

```bash
uv init my-app          # 新建目录并初始化
# 或
uv init                 # 在当前目录初始化
cd my-app
```

生成的文件：

```
my-app/
├── .python-version     # 指定 Python 版本
├── pyproject.toml      # 项目配置与依赖声明
├── README.md
└── main.py             # 示例入口
```

`pyproject.toml` 示例：

```toml
[project]
name = "my-app"
version = "0.1.0"
description = "Add your description here"
requires-python = ">=3.12"
dependencies = []
```

### 2. 指定 Python 版本

```bash
uv python pin 3.12      # 固定版本，写入 .python-version
uv python list          # 查看可用版本
```

### 3. 运行项目

```bash
uv run main.py          # 会自动创建虚拟环境并安装依赖，再运行
uv run python -c "print('hello')"
```

---

## 三、添加 / 移除包

### 添加依赖

```bash
uv add fastapi                          # 添加运行时依赖
uv add "fastapi[standard]"              # 带 extras
uv add langchain langchain-openai       # 一次加多个
uv add --dev pytest ruff                # 开发依赖（写入 [dependency-groups]）
uv add --optional docs mkdocs           # 可选依赖组
```

### 移除依赖

```bash
uv remove fastapi
```

### 查看依赖

```bash
uv tree                    # 依赖树
uv lock                    # 手动锁定，生成 uv.lock
uv sync                    # 按 pyproject.toml + uv.lock 同步环境
```

---

## 四、本项目三个技术栈的常用安装命令

```bash
# FastAPI 后端
uv add fastapi uvicorn[standard] pydantic-settings

# 数据库（进阶阶段）
uv add sqlmodel alembic

# LangChain
uv add langchain langchain-openai langchain-community
uv add langchain-cli          # 可选，脚手架工具
uv add chromadb               # 向量库（RAG 阶段）

# 前端（Streamlit）
uv add streamlit

# 测试与代码质量（开发依赖）
uv add --dev pytest ruff httpx
```

---

## 五、常用命令速查

| 命令 | 作用 |
|------|------|
| `uv init` | 初始化项目 |
| `uv add <pkg>` | 添加依赖 |
| `uv add --dev <pkg>` | 添加开发依赖 |
| `uv remove <pkg>` | 移除依赖 |
| `uv sync` | 同步/重装环境 |
| `uv lock` | 生成/更新 uv.lock |
| `uv run <cmd>` | 在项目环境里执行命令 |
| `uv tree` | 查看依赖树 |
| `uv python pin <ver>` | 固定 Python 版本 |
| `uv pip list` | 列出已装包（pip 兼容接口） |

---

## 六、关键概念

- **虚拟环境**：`uv` 默认在项目下 `.venv/` 创建隔离环境，避免依赖冲突。
- **`uv.lock`**：锁定每个依赖的确切版本，保证「可复现构建」——换台机器 `uv sync` 也能装出一模一样的环境。
- **`uv run` 优于手动激活**：不需要先 `source .venv/bin/activate`，直接 `uv run xxx` 即可，方便且不易出错。
- **依赖分组**：`--dev`（测试/格式化工具）与 `--optional`（可选功能）都写在 `pyproject.toml` 里，结构清晰。

> ⚠️ 记笔记时请把「当前用到的 uv 命令」写下来，尤其是新学的参数，方便以后查。
