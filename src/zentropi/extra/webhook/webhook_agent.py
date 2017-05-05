# coding=utf-8
# coding=utf-8

# coding=utf-8

import asyncio
import ssl

import os
from aiohttp import web
from zentropi import Agent

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


def web_server(emit_callback):
    loop = asyncio.new_event_loop()
    app = web.Application(loop=loop)
    app.router.add_get('/emit', emit_callback)
    host = '127.0.0.1'
    port = 26514
    web.run_app(app, host=host, port=port, loop=loop, ssl_context=get_ssl_context())


class WebhookAgent(Agent):
    def __init__(self, name=None):
        super().__init__(name=name)

    def start(self, loop=None):
        self.spawn_in_thread(web_server, self.webhook_emit)
        super().start(loop)

    async def webhook_emit(self, request):
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
