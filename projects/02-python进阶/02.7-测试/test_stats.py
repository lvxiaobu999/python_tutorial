"""stats 模块的测试（练手文件）

运行：uv run pytest "02.7-测试" -v
示例测试已写好（应通过）；TODO 部分按 02.7 README 的要求补全。
写完每组就跑一次 pytest，让「红 → 绿」的循环转起来。
"""

import pytest

from stats import grade, mean, parse_scores, std


# ============ 示例：普通断言 ============
def test_mean_basic() -> None:
    # AAA 结构：Arrange 准备 / Act 执行 / Assert 断言
    numbers = [1, 2, 3]                     # Arrange
    result = mean(numbers)                  # Act
    assert result == 2                      # Assert


# ============ 示例：异常测试 ============
def test_mean_empty_raises() -> None:
    with pytest.raises(ValueError):
        mean([])


# ============ 示例：参数化 ============
@pytest.mark.parametrize(
    ("score", "expected"),
    [(95, "A"), (59.5, "E")],
)
def test_grade_examples(score: float, expected: str) -> None:
    assert grade(score) == expected


# ============ TODO 1：mean 参数化 ============
@pytest.mark.parametrize(
    ("numbers", "expected"),
    [
        # TODO：补 3 组正常数据，例如 ([2, 4], 3.0)、([5], 5.0)、([-2, 2], 0.0)
    ],
)
def test_mean_params(numbers: list[float], expected: float) -> None:
    raise NotImplementedError("TODO 1：删除这行，补全参数化数据和断言")


# ============ TODO 2：mean 的边界 ============
def test_mean_single() -> None:
    """TODO 2a：单元素列表 mean([5]) 应等于 5.0。"""
    raise NotImplementedError("TODO 2a")


def test_mean_negative() -> None:
    """TODO 2b：含负数 mean([-1, 1]) 应等于 0.0。"""
    raise NotImplementedError("TODO 2b")


# ============ TODO 3：parse_scores ============
def test_parse_scores_ok() -> None:
    """TODO 3a：parse_scores("85, 90,78") 应返回 [85, 90, 78]（含空格、顺序保持）。"""
    raise NotImplementedError("TODO 3a")


def test_parse_scores_raises() -> None:
    """TODO 3b：parse_scores("85,x,90") 应抛 ValueError，且消息里含「第 2 项」。

    提示：with pytest.raises(ValueError) as exc_info: ...，
    然后 assert "第 2 项" in str(exc_info.value)。
    再补一组超范围的：parse_scores("50,120") 消息含「第 2 项」。
    """
    raise NotImplementedError("TODO 3b")


# ============ TODO 4：grade 全边界 ============
@pytest.mark.parametrize(
    ("score", "expected"),
    [
        # TODO：覆盖 9 个边界：59/60/69/70/79/80/89/90/100
        # 提示：60 是 D、90 是 A、59 是 E …… 先自己推一遍再写，测出 bug 才有价值
    ],
)
def test_grade_boundaries(score: float, expected: str) -> None:
    raise NotImplementedError("TODO 4：删除这行，补全断言")


# ============ TODO 5：std 已知值 ============
def test_std_known_value() -> None:
    """TODO 5：先手算 std([2, 4, 4, 4, 5, 5, 7, 9])（答案是 2.0），再断言。

    用 pytest.approx 处理浮点误差：
    assert std(numbers) == pytest.approx(2.0)
    """
    raise NotImplementedError("TODO 5")


# ============ TODO 6（选做）：给前面的章节补测试 ============
# 选一个你在 02.1/02.2 写过的类或函数（如 Vector2D、make_multiplier、retry），
# 新建 test_xxx.py 为它写至少 3 个测试（正常 + 边界 + 异常各一）。
