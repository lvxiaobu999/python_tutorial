# 02.6 依赖与虚拟环境

> 这一章解决「为什么每个项目要一个独立环境、依赖怎么声明才可复现」。你在模块 00/01 已经在**用** uv 了，这里把原理补齐：pyproject.toml 是「意图」，uv.lock 是「事实」。以后进 FastAPI/LangChain 项目，依赖会多起来，这章是地基。

## 知识点速查

### 1. 虚拟环境解决什么问题

没有隔离时，所有项目共用一套全局包：项目 A 要 pytest 8、项目 B 要 9，装哪个都会弄坏另一个。虚拟环境 = 每个项目一个独立的 `site-packages` 目录，本项目的就是 `.venv/`。

```text
全局 Python（不装项目包，保持干净）
├── projects/01-python基础/.venv/   ← 只装 keyboard
└── projects/02-python进阶/.venv/   ← 只装 pytest
```

验证：`uv run python -c "import sys; print(sys.executable)"` 打印的是本项目 `.venv` 里的 python，不是全局的——这就是「活在虚拟环境里」。

### 2. pyproject.toml 逐行解读（本项目真实文件）

```toml
[project]                        # 项目元信息
name = "python-advanced"
version = "0.1.0"
requires-python = ">=3.13"       # 声明需要的 Python 版本，uv 会自动找到/安装
dependencies = [                 # 运行时依赖：跑业务代码必须装的包
    "pytest>=9.1.1",
]

[dependency-groups]              # 开发依赖：只有开发者需要（测试/格式化工具）
dev = [
    "pytest>=9.1.1",
]
```

**dependencies vs dev 组**：用户用你的库不需要 pytest，但你开发时需要——工具类依赖放 dev 组，不污染生产。

### 3. uv.lock：锁定「事实」

- pyproject 写的是**约束**（`pytest>=9`），lock 记录的是**解析结果**（`pytest==9.1.1` + 传递依赖的精确版本 + 哈希值）。
- uv.lock **要提交进 git**：同事或 CI 执行 `uv sync` 时，装出和你**一模一样**的环境——这叫可复现构建（reproducible build）。
- 删掉 lock 重新解析 = 版本漂移，可能引入不兼容——除非有意升级，别删。

### 4. uv 常用命令速查表

| 命令 | 作用 |
|------|------|
| `uv init <目录>` | 新建项目（生成 pyproject.toml、.python-version 等） |
| `uv add <包>` | 添加运行时依赖并写入 pyproject + lock |
| `uv add --dev <包>` | 添加开发依赖（进 dependency-groups.dev） |
| `uv remove <包>` | 移除依赖 |
| `uv sync` | 按 lock 精确安装环境（新机器/CI 第一步） |
| `uv lock` | 只重新解析并更新 lock（升级前跑） |
| `uv lock --upgrade` / `uv add -U <包>` | 升级依赖版本 |
| `uv run <命令>` | 在本项目环境里执行（自动确保环境已同步） |
| `uv tree` | 树状显示依赖关系（谁带进来的谁） |
| `uv python list` | 看机器上可用的 Python 版本 |

### 5. uv run vs 手动激活

```bash
# 方式一（推荐）：uv run 总是确保环境同步后再执行
uv run python xxx.py
uv run pytest

# 方式二：手动激活（老 venv 习惯，一般不需要）
.venv/Scripts/activate     # Windows Git Bash
python xxx.py              # 激活后 python 自动指向 .venv
```

### 6. 版本约束语法速查表

| 写法 | 含义 |
|------|------|
| `pytest>=8,<10` | 大于等于 8 且小于 10（区间） |
| `pytest==9.1.1` | 精确锁定（lock 文件里全是这种） |
| `pytest~=9.1` | 兼容版本：>=9.1, <10.0（锁主版本，允许次版本升级） |
| `pytest` | 无约束，装最新 |

## 易错点

- 绕过 uv 直接 `pip install` 装到全局——本仓库红线；应急时 `uv pip install` 也是装进项目环境，但常规操作用 `uv add`。
- 改了 pyproject.toml 手写依赖却没跑 `uv lock`/`uv sync`——`uv run` 会自动同步兜底，但直接用 `.venv` 里的 python 就不会。
- 把 ruff/pytest 这类工具写进 `[project] dependencies`——生产环境会多装一堆没用的包，放 `--dev`。
- 删 uv.lock「解决」依赖冲突——冲突信息很有价值，该看 `uv tree` 找出谁带进来的。
- 以为 `.venv` 要提交 git——它体积大且可重建（uv.lock + pyproject 就能复原），`.gitignore` 里忽略它。

## 进阶提示

- `uv export --format requirements-txt > requirements.txt`：给还用 pip 工作流的服务器/平台导出传统格式。
- `uv python pin 3.13`：固定项目 Python 版本写入 `.python-version`，团队统一解释器。
- `[project.optional-dependencies]`（extras）：可选功能组，如 `pip install mypkg[web]` 才装 web 相关依赖——读开源库文档常见。
- Docker 部署 FastAPI 时：只 COPY pyproject + lock 先 `uv sync`（利用层缓存），再 COPY 代码，构建又快又可复现。

## 学习顺序与练习

这章以**动手操作**为主：边读速查表边在本项目目录里跑命令，再做 `01-环境体检.py` 的观察任务。

基础 TODO（见 `01-环境体检.py`，命令 + 观察题）：
1. 跑 `uv add --dev ruff`，然后重新运行体检脚本，观察输出的变化（依赖表多了什么？进了哪个组？）。
2. 跑 `uv tree`，把 pytest 的传递依赖树抄进笔记；再解释 iniconfig/pluggy 是怎么来的。
3. 在脚本末尾的注释里用自己的话回答：为什么 uv.lock 要提交进 git，而 .venv 不要？
