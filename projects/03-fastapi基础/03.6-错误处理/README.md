# 03.6 错误处理

> API 出错时，客户端靠两样东西理解发生了什么：**状态码 + 错误详情**。422 校验错误你已经在 03.2/03.3 见过（Pydantic 自动抛的），这一章管剩下的：主动报错（HTTPException）、业务专属错误（自定义异常）、把错误写进文档（responses）。

## 知识点速查

### 1. HTTPException：最常用的报错方式

```python
raise HTTPException(status_code=404, detail="书不存在")
```

- `raise`（不是 return）：立即中断请求处理，FastAPI 把它转成对应状态码的 JSON 响应。
- 响应体：`{"detail": "书不存在"}`；detail 也可以是 dict，前端好做结构化提示。

### 2. 常用状态码速查

| 码 | 含义 | 典型场景 |
|----|------|----------|
| 200 | OK | 查询成功（默认） |
| 201 | Created | 创建成功 |
| 204 | No Content | 删除成功，无响应体 |
| 404 | Not Found | 资源不存在 |
| 422 | Unprocessable Entity | 校验失败（Pydantic 自动） |

### 3. 自定义异常 + 全局处理器
- 业务错误先定义异常类（`class BookNotFoundError(Exception)`），代码里 `raise` 它——含义自解释。
- `@app.exception_handler(XXX)` 注册处理器，统一转成响应。
- 好处：抛错的地方不用关心状态码和响应格式；格式要改只动处理器一处。

### 4. responses 参数：把错误写进文档
`responses={404: {"description": "书不存在"}}` 不改变行为，只让 /docs 显示「这个接口可能返回什么错」——文档完整，前端照着写错误处理。

### 5. 反模式：200 里报错
返回 `{"error": ...}` 但状态码 200 → 客户端必须解析 body 才知道成败，HTTP 语义作废。**状态码是给机器读的契约**，别绕开它。

## 易错点
- `return HTTPException(...)` ❌：必须 `raise`。return 只会把它原样序列化成一个 200 响应体。
- 异常处理器签名固定：`(request: Request, exc: 你的异常)`，两个都要写。
- 204 不能有响应体：`status_code=204` 且 `return None`，别想再捎带数据。
- detail 忘了写 → 客户端只看到干巴巴的状态码，排查全靠猜。

## 进阶提示
- 想统一所有错误的外层格式（比如都包成 `{"code": ..., "message": ...}`）？给 `RequestValidationError` 也注册 handler，连 422 的格式都能改。
- `HTTPException` 有 `headers` 参数：401 附带 `WWW-Authenticate` 头是惯例（04.2 认证章用得上）。

## 学习顺序与练习

启动 `uv run fastapi dev "03.6-错误处理/06-错误处理.py"`，先各触发一次 200/404 对比感受，再完成 TODO：

1. TODO 1：删除接口——存在返回 204，不存在抛 404。
2. TODO 2：自定义业务异常 `PriceTooHighError` + 处理器，并写下状态码的选择理由。
3. TODO 3：在 /docs 里把 200/404/422 各触发一次——这就是期末大作业的验收路径。
