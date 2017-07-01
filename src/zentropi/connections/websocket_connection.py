# coding=utf-8
import ssl
import traceback
from typing import Optional

import os
import websockets

from zentropi import Frame
from ..agent import Agent
from ..connections.connection import Connection
from ..utils import logger, validate_auth, validate_endpoint, validate_name

# logger = log_to_stream(enable=True)
assert Optional  # ignore unused error for now.


class WebsocketConnection(Connection):
    def __init__(self, agent: Agent) -> None:
        super().__init__()
        self._agent = agent
        self._endpoint = ''
        self._spaces = set()
        self._auth = ''
        self.ws = None
        self.timeout = 60 * 5
        self._watchdog_last_value = 0
        self._watchdog_value = 1
        self._watchdog_disable = True
        self._watchdog_running = False
        self._agent.spawn(self.watchdog())

    def bind(self, endpoint: str) -> None:
        raise NotImplementedError('WebsocketConnection does not support bind()')

    def feed_watchdog(self):
        self._watchdog_value += 1

    async def watchdog(self):
        if self._watchdog_running:
            logger.debug('watchdog DOUBLE RUN')
            return
        self._watchdog_running = True
        logger.debug('watchdog sleeping')
        while True:
            await self._agent.sleep(self.timeout)
            if self._watchdog_disable:
                logger.debug('watchdog disabled')
                continue
            if not self._watchdog_last_value < self._watchdog_value:
                logger.debug('watchdog triggered')
                self.close()
                self._agent.spawn(self._connect())
            self._watchdog_last_value = self._watchdog_value

    async def _connect(self, endpoint=None, auth=None):
        self._watchdog_disable = False
        endpoint = endpoint or self._endpoint
        auth = auth or self._auth
        # if endpoint.startswith('wss://zentropi.com'):
        #     cafile = '~/.zentropi/zentropi.com.crt'
        # else:
        #     cafile = '~/.zentropi/self-ssl.crt'
        # cafile = os.path.expanduser(cafile)
        # if endpoint.startswith('wss://'):
        #     ssl_context = ssl.create_default_context(cafile=cafile)
        # else:
        #     ssl_context = None
        if endpoint.endswith('/'):
            endpoint = endpoint[:-1]
        # async with websockets.connect('{}/{}'.format(endpoint, auth), ssl=ssl_context) as websocket:
        async with websockets.connect('{}/{}'.format(endpoint, auth)) as websocket:
            logger.debug('connected')
            self._connected = True
            self.ws = websocket
            while self._connected:
                try:
                    text = await websocket.recv()
                    self.feed_watchdog()
                    frame = Frame.from_json(text)
                    self._agent.handle_frame(frame)
                except websockets.exceptions.ConnectionClosed as e:
                    logger.debug('disconnected {}'.format('; '.join(e.args)))
                    break
            self._connected = False
        logger.debug('closed')

    async def connect(self, endpoint: str, auth: Optional[str] = None) -> None:  # type: ignore
        endpoint = validate_endpoint(endpoint)
        auth = validate_auth(auth)
        self._auth = auth or self._agent._auth
        if self._connected:
            raise ConnectionError('Already connected.')
        if not (endpoint.startswith('wss://') or endpoint.startswith('ws://')):
            raise ValueError('Expected endpoint to begin with "wss://".'
                             'Got: {!r}'.format(endpoint))
        self._endpoint = endpoint
        self._watchdog_disable = False
        logger.debug('connecting')
        self._agent.spawn(self._connect())

    def close(self):
        # todo
        self._connected = False
        logger.debug('closed')
        self._watchdog_disable = True

    async def join(self, space: str) -> None:  # type: ignore
        space = validate_name(space)
        self._spaces.add(space)
        # todo
        pass

    async def leave(self, space: str) -> None:  # type: ignore
        space = validate_name(space)
        self._spaces.remove(space)
        # todo
        pass

    def spaces(self):
        return [s for s in self._spaces]

    async def broadcast(self, frame):
        if not (self.ws and self.ws.open):
            logger.debug('skipping broadcast, not connected')
            return
        try:
            await self.ws.send(frame.as_json())
        except Exception as e:
            traceback.print_exc()
            self.close()
            logger.debug('disconnected')
