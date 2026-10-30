# 03.3 Pydantic 模型

> 03.2 学会了「写函数就是写接口」，这一章是「写模型就是写校验」：`BaseModel` 用字段注解声明数据长什么样，FastAPI 据此自动校验、转换、生成文档。这就是模块 README 说的「Pydantic 是 FastAPI 的灵魂」。

## 知识点速查

### 1. BaseModel：字段 + 注解 = 数据契约

```python
class Book(BaseModel):
    title: str              # 必填
    price: float            # 必填
    in_stock: bool = True   # 有默认值 → 可选
```

- 缺必填字段 / 类型对不上 → 自动 422，错误信息里**指明是哪个字段**。
- 校验通过后字段就是干净的正确类型：JSON 里传 `"45"` 会自动转成 `45.0`。
- `book.model_dump()` 把模型转成 dict（旧教程里的 `.dict()` 是它的前身）。

### 2. Field：给字段加规则

| 写法 | 含义 |
|------|------|
| `Field(gt=0)` | 大于 0（价格必须为正） |
| `Field(ge=1, le=5)` | 1 ≤ x ≤ 5（评分） |
| `Field(min_length=1)` | 字符串至少 1 个字符（拒收空串） |
| `Field(default_factory=list)` | 可变默认值的标准写法（dataclass 同款习惯） |
| `Field(description="...")` | 说明文字，直接显示在 /docs |

### 3. 可选与默认
- `subtitle: str | None = None`：可传可不传，不传是 `None`。
- 「没传」（用默认值）和「传了 null」是两回事，进阶的 `exclude_unset`（03.4）会用到这个区别。

### 4. 嵌套模型
字段类型可以是另一个 `BaseModel`，请求体 JSON 按结构逐层校验；`list[Book]` 表示整批数据。嵌套模型的 `description` 也会进文档。

## 易错点
- `tags: list[str] = []`：在 Pydantic 里其实安全（默认值会被深拷贝），但惯例仍写 `Field(default_factory=list)`——和 dataclass 保持同一习惯，不用记两套规则。
- 边界想清楚：`price: float = Field(ge=0)` 允许 0 元书；要「必须为正」得用 `gt=0`。
- 校验失败的 422 响应里，`loc` 指明哪个字段出错、`msg` 说明错在哪——**读它比猜快**。
- 嵌套模型传成错误结构（author 传成字符串）→ 422 的 `loc` 会指到里层字段。

## 进阶提示
- `EmailStr` 类型开箱即用（`fastapi[standard]` 自带 email-validator），格式不对自动 422。
- Pydantic 独立于 FastAPI，可单独使用：解析配置文件、环境变量都能交给它。
- 字段别名（`alias`）能让对外 JSON 用驼峰、对内用蛇形——读别人项目会见到。

## 学习顺序与练习

启动 `uv run fastapi dev "03.3-pydantic模型/03-模型.py"`，先玩演示接口、故意发非法数据读 422，再完成 TODO：

1. TODO 1：给演示 2 发非法 rating，把 422 里的 `loc` 和 `msg` 抄下来。
2. TODO 2：写 `BookCreate` 模型（期末大作业的核心资产）：title/author 最少 1 字符、price > 0、rating 0~5。
3. TODO 3：给模型加可选字段，区分「不传 / 传 null / 传值」三种请求。
