"""依赖与虚拟环境：环境体检脚本

这章的主战场在命令行，这个脚本负责「让环境看得见」：
打印当前解释器在哪、Python 什么版本、装了哪些包、分别属于哪个依赖组。
做完 README 里的 TODO 后重跑它，观察变化。
"""

import sys
from importlib.metadata import distributions
from pathlib import Path


def main() -> None:
    print("=" * 50)
    print("1. 当前解释器")
    print("=" * 50)
    # uv run 会确保用的是本项目 .venv 里的 python；
    # 路径里包含 .venv 就说明「活在虚拟环境里」。
    print(sys.executable)

    print()
    print("=" * 50)
    print("2. Python 版本")
    print("=" * 50)
    print(sys.version)

    print()
    print("=" * 50)
    print("3. 项目位置（pyproject.toml 应该在这里）")
    print("=" * 50)
    # Path(__file__) 是这个脚本自己，向上两级是项目根目录
    project_root = Path(__file__).resolve().parent.parent
    print(project_root)
    print("pyproject.toml 存在：", (project_root / "pyproject.toml").exists())
    print("uv.lock 存在：", (project_root / "uv.lock").exists())
    print(".venv 存在：", (project_root / ".venv").exists())

    print()
    print("=" * 50)
    print("4. 环境里已安装的包（含传递依赖）")
    print("=" * 50)
    # distributions() 枚举 .venv 里所有包：直接依赖 + 依赖的依赖都在
    for dist in sorted(distributions(), key=lambda d: d.metadata["Name"].lower()):
        print(f"  {dist.metadata['Name']}=={dist.version}")

    print()
    print("提示：完成 README 的 TODO 1（uv add --dev ruff）后重跑本文件，")
    print("     观察第 4 部分多了哪些包；再打开 pyproject.toml 看它们进了哪个组。")


if __name__ == "__main__":
    main()

# ============ TODO（按 02.6 README 完成后在下面写答案） ============
# TODO 2：运行 uv tree，把输出里 pytest 的依赖树抄到这里（注释形式）：
#
# TODO 3：用自己的话回答（写在注释里，每题 1~2 句）：
#   a. 为什么 uv.lock 要提交进 git，而 .venv 不要？
#   b. dependencies 和 dependency-groups.dev 有什么区别？ruff 该放哪个？
