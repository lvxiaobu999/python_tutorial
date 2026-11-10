"""04.5 WebSocket 与流式：让服务器学会「连续说话」

之前的接口都是「一问一答」：请求进来，return 一次，连接就结束。
本章学两种「持续说话」的方式：WebSocket（双向长连接，聊天室的骨架）
和 SSE（服务器单向流式推送，AI 打字机效果的雏形）。

运行（在 projects/04-fastapi进阶 目录下）：
    uv run fastapi dev "04.5-websocket与流式/05-流式.py"
注意：/docs 调试不了 WebSocket（OpenAPI 只描述「请求-响应」），
SSE 在 /docs 里也要等全部推完才显示；请用浏览器打开 http://127.0.0.1:8000/ 。
"""

import asyncio
from pathlib import Path

from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.responses import FileResponse, StreamingResponse

app = FastAPI(title="04.5 WebSocket 与流式练习")


# ============ 演示 1：WebSocket 回声服务（收一条，回一条） ============
# WebSocket 也是路由（03.2 家族新成员），只是装饰器换成 @app.websocket；
# 参数 ws 不是查询参数也不是依赖，而是「这条长连接本身」，收和发全靠它。
@app.websocket("/ws")
async def echo(ws: WebSocket) -> None:
    """在演示页（index.html）发消息：发什么回什么。
    观察运行 fastapi dev 的终端——接入、每条消息、断开各有一条 print。"""
    await ws.accept()  # 握手：服务端「点头」后连接才真正建立，浏览器端才会触发 onopen
    print("→ [WS] 客户端接入")
    try:
        while True:  # 长连接靠 while 保活：不循环的话回一条就退出，退化成普通请求-响应
            text = await ws.receive_text()  # 没消息时挂起等待——02.5 事件循环的日常
            print(f"← [WS] 收到：{text}")
            await ws.send_text(f"回声：{text}")
    except WebSocketDisconnect:
        # 关页面/断网会抛这个异常：这是「正常下班」不是故障，捕获后安静收尾即可
        print("← [WS] 客户端断开")


# ============ 演示 2：SSE 流式推送（打字机效果的骨架） ============
BOOKS = ["三体", "活着", "百年孤独", "围城", "1984"]


async def book_stream():
    """async 生成器 = 02.3 的 yield + 02.5 的 await 合体：
    每准备好一小块就 yield 一块，立刻发往浏览器，绝不攒齐再给。
    未来 LangChain 流式对话，就是把这里的 asyncio.sleep 换成模型吐 token。"""

    count = 0
    for title in BOOKS:
        await asyncio.sleep(
            0.5
        )  # 模拟「生成一条」的耗时（真实场景：查库/调模型卡在这步）
        count += 1
        yield f"data: 《{title}》\n\n"  # SSE 格式：data: 开头，\n\n 两个换行才是一条消息的终点
    yield f"data: 共《{count}》本 \n\n"


@app.get("/books/stream")
async def stream_books() -> StreamingResponse:
    """普通 return 是「做完、攒齐、一次性交付」；StreamingResponse 是「边做边交付」：
    生成器每 yield 一次，就有一块字节流向浏览器。浏览器侧用 EventSource 接收。"""
    return StreamingResponse(book_stream(), media_type="text/event-stream")


# ============ 附：演示页入口（浏览器怎么玩） ============
# 把同目录的 index.html 供出去。必须从 http://127.0.0.1:8000/ 打开（同源），
# 页面里的 EventSource 才不会被浏览器的同源策略拦住（跨域放行是 04.3 CORS 的主题）。
@app.get("/")
def demo_page() -> FileResponse:
    """启动后浏览器访问 http://127.0.0.1:8000/ ，就是本章的练习场。"""
    return FileResponse(Path(__file__).with_name("index.html"))


# ============ TODO 1：ConnectionManager 多人广播 ============
# 写一个 ConnectionManager 类：connect() 收编连接、disconnect() 移除、broadcast() 群发；
# 再加 @app.websocket("/ws/chat")：收到消息后 broadcast 给所有连接——
# 一个人发言全场可见，简易聊天室就成了。
class ConnectionManager:
    """聊天室中枢：维护「当前在线的所有连接」。

    WebSocket 只能一对一说话；「群发」= 自己攥着一份连接名单，挨个 send。
    三个方法对应一段连接的生命周期：接入登记 → 在线群发 → 断开销户。
    """

    def __init__(self) -> None:
        self.active: list[WebSocket] = (
            []
        )  # 在线名册：群发要「挨个说话」，就得攥着每条连接

    async def connect(self, ws: WebSocket) -> None:
        await ws.accept()  # 握手挪进 connect：从这走進来的连接保证都已点头生效
        self.active.append(ws)
        print(f"→ [CHAT] 客户端接入，当前在线 {len(self.active)} 人")

    def disconnect(self, ws: WebSocket) -> None:
        # 同步方法：列表增删不需要 await；只有「说话」（accept/send）才是异步的
        self.active.remove(ws)
        print(f"← [CHAT] 客户端断开，当前在线 {len(self.active)} 人")

    async def broadcast(self, text: str) -> None:
        # 遍历副本（.copy()）：await 的间隙可能有人断线销户，正遍历的名单被动过会乱套
        for ws in self.active.copy():
            await ws.send_text(text)


manager = (
    ConnectionManager()
)  # 模块级单例（04.1 engine 的老套路）：全应用共享一份在线名单


@app.websocket("/ws/chat")
async def chat(ws: WebSocket) -> None:
    """简易聊天室：任何人发言，全场（包括发言者自己）都能收到。
    断线处理沿用演示 1：receive 抛 WebSocketDisconnect 是「正常下班」，销户再广播一声。"""
    await manager.connect(ws)
    try:
        while True:
            text = await ws.receive_text()
            await manager.broadcast(text)
    except WebSocketDisconnect:
        manager.disconnect(ws)
        await manager.broadcast("（一位朋友离开了聊天室）")


# ============ TODO 2：带总数的 SSE ============
# 给 /books/stream 升级：书名照推，流末尾再补一条 data: 共 5 本\n\n，
# 让前端能显示「加载完成」。提示：for 循环结束后再 yield 一次即可。

# ============ TODO 3：思考题 ============
# 什么场景必须 WebSocket 而不能用 SSE？提示：SSE 只能服务器→浏览器单向推，
# 想想「双方都要说话」的场景（聊天室、协同编辑），把答案写进学习笔记。
