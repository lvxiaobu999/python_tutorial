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
    numbers: list[float] = [1, 2, 3]  # Arrange（显式标注：否则推断为 list[int]，
    # 而 list 不变型——list[int] 不能传给 list[float] 参数，Pylance 会标红）
    result = mean(numbers)  # Act
    assert result == 2  # Assert


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
    ("numbers", "expected"), [([2, 4], 3.0), ([5], 5.0), ([-2, 2], 0.0)]
)
def test_mean_params(numbers: list[float], expected: float) -> None:
    assert mean(numbers) == expected


# ============ TODO 2：mean 的边界 ============
def test_mean_single() -> None:
    """TODO 2a：单元素列表 mean([5]) 应等于 5.0。"""
    assert mean([5]) == 5.0


def test_mean_negative() -> None:
    """TODO 2b：含负数 mean([-1, 1]) 应等于 0.0。"""
    assert mean([-1, 1]) == 0.0


# ============ TODO 3：parse_scores ============
def test_parse_scores_ok() -> None:
    """TODO 3a：parse_scores("85, 90,78") 应返回 [85, 90, 78]（含空格、顺序保持）。"""

    assert parse_scores("85, 90,78") == [85, 90, 78]


def test_parse_scores_raises() -> None:
    """TODO 3b：parse_scores("85,x,90") 应抛 ValueError，且消息里含「第 2 项」。

    提示：with pytest.raises(ValueError) as exc_info: ...，
    然后 assert "第 2 项" in str(exc_info.value)。
    再补一组超范围的：parse_scores("50,120") 消息含「第 2 项」。
    """
    with pytest.raises(ValueError) as exc_info:  # as exc_info：接住刚抛出的异常对象
        parse_scores("85,x,90")
    assert "第 2 项" in str(exc_info.value)

    # 更省事的等价写法：pytest.raises(ValueError, match="第 2 项")，match 是正则
    with pytest.raises(ValueError) as exc_info:
        parse_scores("50,120")
    assert "第 2 项" in str(exc_info.value)


# ============ TODO 4：grade 全边界 ============
@pytest.mark.parametrize(
    ("score", "expected"),
    [
        (59, "E"),
        (60, "D"),
        (69, "D"),
        (70, "C"),
        (79, "C"),
        (80, "B"),
        (89, "B"),
        (90, "A"),
        (100, "A"),
    ],
)
def test_grade_boundaries(score: float, expected: str) -> None:
    assert grade(score) == expected


# ============ TODO 5：std 已知值 ============
def test_std_known_value() -> None:
    """TODO 5：先手算 std([2, 4, 4, 4, 5, 5, 7, 9])（答案是 2.0），再断言。

    用 pytest.approx 处理浮点误差：
    assert std(numbers) == pytest.approx(2.0)
    """
    numbers: list[float] = [2, 4, 4, 4, 5, 5, 7, 9]  # 标注原因同 test_mean_basic
    assert std(numbers) == pytest.approx(2.0)


# ============ TODO 6（选做）：给前面的章节补测试 ============
# 选一个你在 02.1/02.2 写过的类或函数（如 Vector2D、make_multiplier、retry），
# 新建 test_xxx.py 为它写至少 3 个测试（正常 + 边界 + 异常各一）。
