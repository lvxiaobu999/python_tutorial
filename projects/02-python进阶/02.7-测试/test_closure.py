"""02.2 练习代码的测试（TODO 6 选做）

被测对象在 02.2-装饰器与闭包/01-闭包与装饰器.py——文件名以数字开头且含连字符，
不是合法的模块名，无法直接 import，只能用 importlib 按路径加载。
它是「练习脚本」而不是「模块」：加载时会执行全部顶层演示代码（打印 + 睡眠），
所以测试会慢几秒、输出会杂一点——这正是「练习代码」与「可复用模块」的区别。
"""

import importlib.util
from pathlib import Path

import pytest

_spec = importlib.util.spec_from_file_location(
    "closure_and_decorators",
    Path(__file__).resolve().parent.parent / "02.2-装饰器与闭包" / "01-闭包与装饰器.py",
)
assert _spec is not None and _spec.loader is not None  # 类型收窄：告诉 pyright 两者非 None
mod = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(mod)  # 此刻会看到 02.2 的演示输出，属预期


# ============ 正常：闭包工厂各自记住自己的 n ============
def test_multiplier_normal() -> None:
    double = mod.make_multiplier(2)
    triple = mod.make_multiplier(3)
    assert double(5) == 10
    assert triple(5) == 15


# ============ 边界：0 与负数的乘法工厂 ============
def test_multiplier_edge() -> None:
    assert mod.make_multiplier(0)(99) == 0
    assert mod.make_multiplier(-2)(3) == -6


# ============ 异常：retry 重试耗尽后，原样上抛最后一个异常 ============
def test_retry_exhausts() -> None:
    calls = {"n": 0}

    @mod.retry(times=3)
    def always_fail() -> None:
        calls["n"] += 1
        raise RuntimeError("总是失败")

    with pytest.raises(RuntimeError, match="总是失败"):
        always_fail()
    assert calls["n"] == 3  # 总共尝试次数 = times


# ============ 加练：retry 前几次失败、最后一次成功 ============
def test_retry_succeeds_later() -> None:
    state = {"n": 0}

    @mod.retry(times=3)
    def flaky() -> str:
        state["n"] += 1
        if state["n"] < 3:
            raise ConnectionError(f"第 {state['n']} 次")
        return "成功"

    assert flaky() == "成功"
    assert state["n"] == 3
