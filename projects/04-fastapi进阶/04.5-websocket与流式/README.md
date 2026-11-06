# 04.5 WebSocket 与流式

> 之前的接口都是「一问一答」，return 完连接就散。本章让服务器学会「连续说话」：WebSocket 双向（聊天室），SSE 单向服务器推（AI 打字机）——模块 06/09 流式对话的地基。

## 知识点速查

### 1. WebSocket 生命周期：accept → 收发循环 → 断开

```python
@app.websocket("/ws")            # 路由家族新成员（03.2），但参数是「连接本身」
async def echo(ws: WebSocket):
    await ws.accept()            # 1) 握手：服务端点头，连接才算建立
    try:
        while True:              # 2) while 保活，循环收发
            text = await ws.receive_text()   # 没消息就挂起（02.5 事件循环）
            await ws.send_text(f"回声：{text}")
    except WebSocketDisconnect:  # 3) 客户端离开，异常收尾，不是故障
        print("断开")
```

### 2. SSE 报文格式：`data: ...\n\n`

```python
yield f"data: 《三体》\n\n"   # 两个 \n 才是一条消息的终点，浏览器 onmessage 才触发
```

由 **async 生成器**产出——就是 02.3 的 yield 与 02.5 的 await 合体：每 yield 一块就推一块。

### 3. StreamingResponse vs 普通 return

```python
return StreamingResponse(book_stream(), media_type="text/event-stream")
```

普通 return：函数做完、攒齐、一次性交付。StreamingResponse：接收生成器，每 yield 一次就往浏览器推一块字节——「边做边交付」，前端才能看到逐条蹦出。

### 4. WS vs SSE 怎么选

| 维度 | WebSocket | SSE |
|------|-----------|-----|
| 方向 | 双向 | 单向（服务器 → 浏览器） |
| 自动重连 | 要自己写 | EventSource 内置 |
| 代理/网关友好度 | 差（需协议升级 Upgrade） | 好（就是普通 HTTP 响应） |
| 典型场景 | 聊天、协同编辑、游戏 | AI 流式输出、行情、通知 |

AI 流式输出几乎都用 SSE：只「推」答案，不需要每吐一个字都双向握手。

## 易错点

- SSE 忘写 `\n\n`：浏览器永远收不到「完整一条」，onmessage 不触发，页面像没反应。
- 某些代理/网关会缓冲 SSE 响应，出现「卡住不出字」——本地没事，上线（nginx 等）要关缓冲。
- 断开后还 `send_text` 会抛异常：收发循环里要捕获 `WebSocketDisconnect`，断开即退出循环。
- EventSource 只能发 GET、带不了自定义请求头；要双向或复杂鉴权就换 WebSocket。
- `/docs` 调试不了 WebSocket（OpenAPI 只描述「请求-响应」），SSE 也等全量才显示，
  必须用浏览器打开 <http://127.0.0.1:8000/> 练。

## 进阶提示

- 本章是模块 05（前端流式展示）和模块 06/09（LangChain 流式对话）的直接地基：
  LangChain 的 `stream()/astream()` 逐个吐 token，后端用本章 SSE 形态转发给前端，就是打字机。
- TODO 1 的 ConnectionManager（connect/disconnect/broadcast）是 FastAPI 官方聊天室示例的标准结构。

## 学习顺序与练习

1. 启动 `uv run fastapi dev "04.5-websocket与流式/05-流式.py"`。
2. 浏览器打开 <http://127.0.0.1:8000/>（`/` 路由供出同目录 index.html，同源才不被 CORS 拦）：
   上半区发消息看回声，下半区点「开始接收图书流」看逐条蹦出，对照终端 print。
3. 完成 TODO：
   - TODO 1：`ConnectionManager`（connect/disconnect/broadcast）+ `/ws/chat`，多人广播。
   - TODO 2：SSE 流末尾追加 `data: 共 N 本`，让前端知道「完了」。
   - TODO 3（思考）：什么场景必须 WebSocket 而不能用 SSE？答案写进学习笔记。
