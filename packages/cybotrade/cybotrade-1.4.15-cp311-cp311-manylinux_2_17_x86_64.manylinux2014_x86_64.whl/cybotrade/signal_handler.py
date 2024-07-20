import logging
import asyncio
from cybotrade.server import WebServer


class SignalHandler:
    server: WebServer | None = None
    def __init__(self):
        print("initing")

    async def on_init(self):
        self.server = WebServer(self, logger=logging.Logger(name="signal"))
        await self.server.start()

    async def on_signal(self):
        print("haha")
