# 模块 02 · Python 进阶

> 目标：掌握面向对象、类型注解与异步，为 FastAPI 打基础。

## 章节清单

| 章节 | 主题 |
|------|------|
| 02.1 面向对象 | 类与实例、继承、多态、魔术方法、dataclass |
| 02.2 装饰器与闭包 | 闭包、@decorator、常用装饰器 |
| 02.3 迭代器与生成器 | __iter__、yield、生成器表达式 |
| 02.4 类型注解 | typing、Optional/Union/Generic、TypeAlias |
| 02.5 异步编程 | async/await、asyncio、事件循环、并发 vs 并行 |
| 02.6 依赖与虚拟环境 | pyproject.toml、依赖锁定、可复现构建 |
| 02.7 测试 | pytest、断言、fixture、mock |

## 学习要点

- **类型注解**是读懂 FastAPI 源码的钥匙：`Optional[T]`、`Union`、泛型必须会用。
- **asyncio**：理解 `async def` / `await` 为何让 FastAPI 高并发，事件循环是什么。
- **pytest**：从本阶段起，练习代码尽量配测试，养成习惯。

## 练习方向

给一个小模块写完整 pytest 测试；用 `async def` 写一个并发抓取任务。

## 笔记文件命名

```
02.1-面向对象.md
02.4-类型注解.md
02.5-异步编程.md
...
```
