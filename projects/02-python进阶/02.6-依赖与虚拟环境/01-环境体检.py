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


# 运行指令（uv 从当前目录逐级向上找 pyproject.toml，所以要先进入项目目录）：
#   cd projects\02-python进阶
#   uv run python 02.6-依赖与虚拟环境\01-环境体检.py
# 若直接在仓库根目录跑 uv run，找不到 pyproject.toml 就会落到全局 Python——
# 体检第 1 项的路径里看不到 .venv 就是这个原因（uv tree 同理也会报错）。
if __name__ == "__main__":
    main()

# ============ TODO（按 02.6 README 完成后在下面写答案） ============
# TODO 2：运行 uv tree，把输出里 pytest 的依赖树抄到这里（注释形式）：
# （在 projects/02-python进阶 目录下运行——uv tree 和 uv run 一样从当前目录
#   逐级向上找 pyproject.toml，在仓库根目录跑会因为找不到项目而报错）
#
# python-advanced v0.1.0
# ├── pytest v9.1.1                  ← [project] dependencies 里的直接依赖
# │   ├── colorama v0.4.6            （Windows 终端的颜色输出支持）
# │   ├── iniconfig v2.3.0           （解析 pytest.ini / pyproject 里的 pytest 配置）
# │   ├── packaging v26.3            （版本号与依赖约束的解析）
# │   ├── pluggy v1.6.0              （pytest 插件系统的内核）
# │   └── pygments v2.21.0           （测试输出/报错信息的语法高亮）
# ├── pyright v1.1.414 (group: dev)
# │   ├── nodeenv v1.11.0
# │   └── typing-extensions v4.16.0
# └── ruff v0.17.3 (group: dev)      ← 零依赖：独立二进制轮子，没有传递依赖
#
# iniconfig / pluggy 的来源：它们是 pytest 的「传递依赖」——uv add pytest 时
# 解析器自动把它们的精确版本写进 uv.lock 并装进环境，从不需要手装。

# TODO 3：用自己的话回答（写在注释里，每题 1~2 句）：
#   a. 为什么 uv.lock 要提交进 git，而 .venv 不要？
###
# 因为uv.lock文件可以确保团队引用的包锁定到同一个版本，避免出现差异导致bug出现。
# 而.venv是虚拟环境，里面存入大量的依赖包，导致文件体积很大，不宜存放到远程git
# 补充：.venv 更关键的性质是「可重建」——拿到 pyproject.toml + uv.lock 跑 uv sync
# 就能复原一模一样的环境；且其内部结构是平台相关的（Windows 是 Scripts\，Linux 是 bin/），
# 跨机器根本不可用，提交了也没意义。
# ###

#   b. dependencies 和 dependency-groups.dev 有什么区别？ruff 该放哪个？
#   dependencies是生产环境所需依赖包
#   dependency-groups.dev是开发环境所需依赖包
#   ruff 属于「只有开发者用」的工具 → 放 dev 组（uv add --dev ruff）
#   实际区别：别人安装你的包时只装 dependencies，dev 组不会跟着装
#
# #
