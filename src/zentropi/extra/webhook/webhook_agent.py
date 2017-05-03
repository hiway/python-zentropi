# coding=utf-8
# coding=utf-8

# coding=utf-8

import asyncio
import os
from aiohttp import web
from zentropi import Agent


TOKEN = os.getenv('ZENTROPI_WEBHOOK_TOKEN', None)
assert TOKEN, 'Error: export ZENTROPI_WEBHOOK_TOKEN="[32-or-more-random-characters]" and pass as ?token="" in request.'


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
        if 'name' not in request.GET:
            return web.json_response({'success': False, 'message': 'Error: required parameter "name" not found.'})
        if 'token' not in request.GET:
            return web.json_response({'success': False, 'message': 'Error: required parameter "token" not found.'})
        name = request.GET['name']
        token = request.GET['token']
        if token != TOKEN:
            return web.json_response({'success': False, 'message': 'Error: authentication failed. Invalid token.'})
        data = {k: v for k, v in request.GET.items() if k not in ['name', 'token']}
        self.emit(name, data=data)
        return web.json_response({'success': True})
