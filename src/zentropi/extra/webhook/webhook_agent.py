# coding=utf-8
import ssl
import json

import os
import hmac
from aiohttp import web
from hashlib import sha1

from zentropi import (
    Agent,
    on_event
)

RELATIVE_BASE_DIR = '~/.zentropi/'
BASE_DIR = os.path.abspath(os.path.expanduser(RELATIVE_BASE_DIR))
TOKEN = os.getenv('ZENTROPI_WEBHOOK_TOKEN', None)
assert TOKEN, 'Error: export ZENTROPI_WEBHOOK_TOKEN="[32-or-more-urlsafe-random-characters]" ' \
              'Send the token with client-request as /emit?token=[32-or-more-urlsafe-random-characters].'


def get_ssl_context():
    cert_path = os.path.join(BASE_DIR, 'webhook.crt')
    key_path = os.path.join(BASE_DIR, 'webhook.key')
    if not os.path.exists(cert_path):
        raise ValueError('Certificate file does not exist: {cert_path}'.format(cert_path=cert_path))
    if not os.path.exists(key_path):
        raise ValueError('Key file does not exist: {key_path}'.format(key_path=key_path))
    ssl_context = ssl.SSLContext(ssl.PROTOCOL_SSLv23)
    try:
        ssl_context.load_cert_chain(cert_path, key_path)
    except Exception as e:
        import traceback
        traceback.print_stack()
        traceback.print_exc()
    return ssl_context


class WebhookAgent(Agent):
    def __init__(self, name=None):
        super().__init__(name=name)
        self.server_task = None
        self.host = '127.0.0.1'
        self.port = 26514
        self.app = None  # type: web.Application
        self.handler = None

    def _add_routes(self):
        self.app.router.add_route('*', '/emit', self.webhook_emit)
        self.app.router.add_route('*', '/{name}', self.webhook_emit)
        self.app.router.add_route('*', '/{name}/{token}', self.webhook_emit)

    async def _run_forever(self):
        self.app = web.Application()
        self._add_routes()
        self.handler = self.app.make_handler()
        server_coro = self.loop.create_server(self.handler,
                                              host=self.host,
                                              port=self.port,
                                              ssl=get_ssl_context())
        self.server_task = await server_coro
        await super()._run_forever()

    async def webhook_emit(self, request):
        name = request.match_info.get('name', None)
        token = request.match_info.get('token', None)
        post_data = await request.post()
        if not name:
            if 'name' not in request.GET or 'name' not in post_data:
                return web.json_response({'success': False, 'message': 'Error: required parameter "name" not found.'})
        if not token and not any(['token' not in request.GET, 'X-Hub-Signature' not in request.headers]):
            return web.json_response({'success': False, 'message': 'Error: required parameter "token" not found.'})
        if not name:
            name = request.GET.get('name', None) or post_data['name']
        if not token:
            token = request.GET.get('token', None)
        if token != TOKEN is False:
            return web.json_response({'success': False, 'message': 'Error: authentication failed. Invalid token.'})
        data = {k: v for k, v in request.GET.items() if k not in ['name', 'token']}
        if post_data:
            data.update({k: v for k, v in post_data.items() if k not in ['name', 'token']})
        self.emit(name, data=data)
        return web.json_response({'success': True})

    @on_event('*** stopping')
    async def on_stopping(self, event):
        print('*** Stop webhook server')
        await self.server_task.wait_closed()
        await self.app.shutdown()
        await self.handler.shutdown(10.0)
        await self.app.cleanup()
