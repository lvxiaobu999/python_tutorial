"""M6 · 多房间连接管理器——04.5 单房间 ConnectionManager 的进阶

变化只有一处本质：在线名单从「一份」变「每板一份」——
04.5:  self.active: list[WebSocket]
现在:  self.rooms: dict[int, list[WebSocket]]   # board_id → 该板的连接们

三个方法的生命周期分工不变：接入登记 → 在线群发 → 断开销户。
broadcast(board_id, payload) 只发给该板的连接——这就是「房间」。

模块级单例照旧（engine 的老套路）：全应用共享同一份名单。
"""

from fastapi import WebSocket


class ConnectionManager:
    def __init__(self) -> None:
        # TODO M6：self.rooms: dict[int, list[WebSocket]] = {}
        ...

    async def connect(self, board_id: int, ws: WebSocket) -> None:
        """握手（accept）+ 上该板名单。"""
        raise NotImplementedError("M6：对照 04.5 connect，多了按 board_id 归组")

    def disconnect(self, board_id: int, ws: WebSocket) -> None:
        """销户。同步方法：列表增删不需要 await（04.5 的观察）。"""
        raise NotImplementedError("M6：从对应房间的名单移除")

    async def broadcast(self, board_id: int, payload: dict) -> None:
        """只对该板名单群发；遍历副本（.copy()）防 await 间隙名单被改（04.5 的坑）。"""
        raise NotImplementedError("M6：ws.send_json(payload) 挨个发")


manager = ConnectionManager()  # 模块级单例：全应用共享一份房间表
