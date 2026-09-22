"""被测模块：成绩统计工具（已实现好，供 test_stats.py 练习测试）

全程带类型注解（呼应 02.4）。测试的目标是验证「外部行为」：
给定什么输入，应返回什么结果 / 抛什么异常。
"""


def mean(numbers: list[float]) -> float:
    """求平均分。空列表抛 ValueError。"""
    if not numbers:
        raise ValueError("不能对空列表求平均")
    return sum(numbers) / len(numbers)


def std(numbers: list[float]) -> float:
    """求总体标准差。

    公式：sqrt( sum((x - 平均值)^2) / n )。
    空列表抛 ValueError。
    """
    avg = mean(numbers)                      # 复用 mean：空列表同样抛 ValueError
    variance = sum((x - avg) ** 2 for x in numbers) / len(numbers)
    return variance ** 0.5


def parse_scores(text: str) -> list[int]:
    """解析 "85,90,78" 这样的逗号分隔分数串，返回 [85, 90, 78]。

    规则：
    - 每项必须是 0~100 的整数（允许首尾空白，如 " 85 "）；
    - 任何一项不合法就抛 ValueError，消息要指出是第几项、收到什么。
    """
    scores: list[int] = []
    for index, part in enumerate(text.split(","), start=1):
        part = part.strip()
        try:
            value = int(part)
        except ValueError:
            raise ValueError(f"第 {index} 项不是整数：{part!r}") from None
        if not 0 <= value <= 100:
            raise ValueError(f"第 {index} 项超出 0~100 范围：{value}")
        scores.append(value)
    return scores


def grade(score: float) -> str:
    """分数转等级：>=90 A；>=80 B；>=70 C；>=60 D；否则 E。"""
    if score >= 90:
        return "A"
    if score >= 80:
        return "B"
    if score >= 70:
        return "C"
    if score >= 60:
        return "D"
    return "E"
