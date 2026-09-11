# 模块 00 · 环境搭建

> 目标：能用 `uv` 建项目、加包、跑通 Hello World，配好 VSCode 与 Git。

## 子目录 / 文件

- [uv使用指南.md](./uv使用指南.md) — uv 安装、建项目、加包完整教程
- （笔记）`00.1-python环境.md`、`00.3-ide配置.md`、`00.4-git基础.md` 等

## 学习要点

1. 装好 Python + uv，理解解释器与虚拟环境的关系。
2. 跑通 `uv init` → `uv add` → `uv run` 的完整闭环。
3. VSCode 装 Python/Pylance 扩展，配好 ruff 格式化和调试器。
4. Git 基本操作 + 写好 `.gitignore`（忽略 `.venv/`、`__pycache__/`）。

## 验收标准

```bash
uv run python -c "print('hello')"   # 能正常输出 hello
```
