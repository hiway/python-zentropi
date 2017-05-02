# coding=utf-8
# coding=utf-8

# coding=utf-8

import asyncio

from aiohttp import web
from zentropi import Agent


def web_server(emit_callback):
    loop = asyncio.new_event_loop()
    app = web.Application(loop=loop)
    app.router.add_get('/emit', emit_callback)
    host = '127.0.0.1'
    port = 26514
    web.run_app(app, host=host, port=port, loop=loop)


class WebhookAgent(Agent):
    def __init__(self, name=None):
        super().__init__(name=name)

    def start(self, loop=None):
        self.spawn_in_thread(web_server, self.webhook_emit)
        super().start(loop)

    def webhook_emit(self, request):
        if 'name' in request.GET:
            name = request.GET['name']
        else:
            return web.json_response({'success': False, 'message': 'Error: required parameter "name" not found.'})
        data = {k: v for k, v in request.GET.items() if k != 'name'}
        self.emit(name, data=data)
        return web.json_response({'success': True})
