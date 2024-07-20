import logging
from aiohttp import web

class WebServer():
    def __init__(self, strategy, logger: logging.Logger):
        self.strategy = strategy
        self.logger = logger
        # self.database_url = environ["DATABASE_URL"]
        # self.secret_key = environ["SECRET_KEY"]
        self.should_start = False

    async def start(self):
        app = web.Application()
        app.add_routes([web.get('/', self.on_signal())])
        logging.info("Starting WebServer")
        await web._run_app(app, port=8001, access_log=self.logger)

    def on_signal(self):
        async def handler(req: web.Request) -> web.StreamResponse:
            x = await req.text()
            print(x)
            await self.strategy.on_signal() 
            resp = web.Response(text="haha")  
            resp.set_status(200)
            return resp
        return handler
