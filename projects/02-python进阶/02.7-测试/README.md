# 02.7 测试

> 这一章解决「怎么证明代码是对的，以及改了之后没改坏」。pytest 是 Python 事实标准的测试框架，也是本模块的验收方式。**从这章起，练习代码尽量配测试**——这个习惯会一路带进 FastAPI（TestClient）和项目实战。

## 知识点速查

### 1. 为什么测试 + pytest 约定

测试是「可重复执行的证明」：改代码后跑一遍，几秒钟知道有没有改坏；读测试也是最快的了解模块用法的方式。

pytest 的**自动发现规则**（遵守约定零配置）：

| 对象 | 命名约定 | 例子 |
|------|----------|------|
| 测试文件 | `test_*.py` 或 `*_test.py` | `test_stats.py` |
| 测试函数 | `test_` 开头 | `test_mean_basic()` |
| 测试类 | `Test` 开头，不带 `__init__` | `TestGrade` |

```bash
uv run pytest                    # 跑当前目录下所有测试
uv run pytest -v                 # 显示每个测试名
uv run pytest -k "grade"         # 只跑名字含 grade 的测试
uv run pytest "02.7-测试/test_stats.py::test_mean_basic"   # 精确到单个测试
```

### 2. 断言：assert

```python
def test_mean_basic():
    result = mean([1, 2, 3])
    assert result == 2           # 失败时 pytest 自动展示 2 != 2.01 这种左右值对比
    assert result == 2, "平均值应为 2"    # 第二个参数：失败时的人类可读说明
```

不需要 `self.assertEqual` 那套（那是 unittest），裸 `assert` 即可，pytest 会把失败现场展示得很清楚。

### 3. 测异常：pytest.raises（呼应 01.7）

```python
import pytest

def test_mean_empty_raises():
    with pytest.raises(ValueError):      # 断言「这个代码块里会抛 ValueError」
        mean([])

def test_parse_error_message():
    with pytest.raises(ValueError) as exc_info:
        parse_scores("85,x,90")
    assert "第 2 项" in str(exc_info.value)   # 还能进一步检查错误消息内容
```

### 4. 参数化：一份代码测多组

```python
@pytest.mark.parametrize(
    ("score", "expected"),
    [(95, "A"), (85, "B"), (75, "C"), (65, "D"), (59, "E")],
)
def test_grade(score, expected):
    assert grade(score) == expected    # 5 组数据 = 5 个独立测试，哪组挂了一目了然
```

边界值思维：`59/60`、`69/70`、`0`、`100` 这些「刚好压线」的值最容易藏 bug，必须覆盖。

### 5. fixture：测试的准备与收尾

```python
import pytest

@pytest.fixture
def sample_scores() -> list[float]:
    return [80, 90, 100]        # 函数名 = fixture 名


def test_mean_with_fixture(sample_scores):   # 参数名和 fixture 名一致 → 自动注入
    assert mean(sample_scores) == 90


@pytest.fixture
def temp_file(tmp_path):         # tmp_path 是 pytest 内置 fixture：临时目录
    path = tmp_path / "data.txt"
    path.write_text("hello", encoding="utf-8")
    return path


# yield 版：yield 前是准备，后是清理（类似 try/finally）
@pytest.fixture
def managed_resource():
    resource = open_resource()
    yield resource               # 测试在这里拿到 resource 运行
    resource.close()             # 测试结束后执行（无论成败）
```

- fixture 也能依赖别的 fixture（如 `temp_file` 用了 `tmp_path`）——和 FastAPI 的 `Depends` 依赖链是同一个思想（模块 03 伏笔）。
- 多个测试共享的 fixture 放同目录的 `conftest.py`，不用 import 直接用。

### 6. mock：把「不可控」变「可控」

测「随机数、当前时间、网络请求」时结果不可复现——mock 用假实现替换掉它们。

```python
def test_with_fake_time(monkeypatch):     # monkeypatch：pytest 内置
    monkeypatch.setattr("time.time", lambda: 1_000_000.0)   # 冻结时间
    assert current_timestamp() == 1_000_000.0
```

原则：**测自己的逻辑，mock 掉外部世界**（网络、时钟、随机）。更复杂的场景用 `unittest.mock.patch`。

### 7. 测试的结构：AAA

```python
def test_withdraw_insufficient():
    # Arrange（准备）：造数据、建对象
    account = BankAccount("小明", 100)
    # Act（执行）：调用被测行为
    with pytest.raises(ValueError):
        account.withdraw(200)
    # Assert（断言）：验证结果（这里验证的是「抛了异常」）
```

一个测试只测一件事；测试名说清「测什么行为 + 什么条件」；测试之间互不依赖（谁先谁后结果一样）。

## 易错点

- 测试函数里**忘写 assert**（只调用了函数）——测试永远绿，等于没测。
- 测试间共享可变全局变量，一个测试改了状态影响下一个，单独跑能过、一起跑就挂。
- 想测「不抛异常」却写成 `try/except: pass`——异常被吞了 assert 根本没执行；直接裸调用 + assert 结果即可。
- fixture 名和测试参数名不一致 → 报 `fixture 'xxx' not found`。
- 只测正常路径；边界（空列表、0、None）和异常路径才是 bug 藏身处。
- 测实现细节（内部调了几次什么）而不是外部行为——重构就崩，测试该保护「契约」。

## 进阶提示

- 覆盖率：`uv add --dev pytest-cov` → `uv run pytest --cov=. --cov-report=term-missing`，看哪些行从没被测过。
- 测协程：直接在测试里 `asyncio.run(fetch(...))` 把异步包成同步再断言（复杂场景再上 pytest-asyncio）。
- TDD（测试驱动开发）：先写测试（红）→ 写实现让它通过（绿）→ 重构。小任务用非常顺手。
- FastAPI 的 TestClient（模块 04）基于 httpx，能不起端口直接测路由——本节思想平移过去而已。

## 学习顺序与练习

先读 `stats.py`（被测模块，已实现好，全程带类型注解——呼应 02.4），跑 `uv run pytest -v` 看两个示例测试通过；然后完成 `test_stats.py` 里的 TODO，从参数化开始练。**这就是模块验收大作业的必做项 1**。

基础 TODO（见 `test_stats.py`）：
1. `test_mean_params`：参数化测 `mean` 的 3 组正常输入。
2. `test_mean_single`：单元素列表；`test_mean_negative`：含负数。
3. `test_parse_scores_ok`：正常解析 + 顺序保持；`test_parse_scores_raises`：非法项抛 ValueError 且消息含位置。
4. `test_grade_boundaries`：参数化覆盖 59/60/69/70/79/80/89/90/100 这 9 个边界。
5. `test_std`：算一组已知数据的总体标准差（先手算好期望值再断言）。
6. 选做：给 02.1 的 `Vector2D` 或 02.2 的 `make_multiplier` 也写上测试。
