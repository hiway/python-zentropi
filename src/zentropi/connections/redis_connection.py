# coding=utf-8
import asyncio
from typing import Optional

import aioredis

from ..agent import Agent
from ..connections.connection import Connection
from ..frames import Frame
from ..utils import validate_endpoint
from ..utils import validate_name

assert Optional  # ignore unused error for now.


class RedisConnection(Connection):
    def __init__(self, agent: Agent) -> None:
        super().__init__()
        self._subscriber = None  # type: ignore
        self._publisher = None  # type: ignore
        self._connection = None  # type: ignore
        self._agent = agent
        self._endpoint = None  # type: Optional[str]
        self._spaces = set()  # type: set
        self._listener_task = None

    async def _connection_listener(self):
        connection = self._connection
        while await connection.wait_message() and self._connected:
            frame_as_dict = await connection.get_json()
            if not frame_as_dict:
                break
            frame = Frame.from_dict(frame_as_dict)
            # print('*** redis: incoming frame',
            #       self._agent.name, frame.source,  frame.name, frame.data)
            self._agent.handle_frame(frame)
        print('*** redis disconnected')

    def bind(self, endpoint: str) -> None:
        self.connect(endpoint)

    async def connect(self, endpoint: str) -> None:  # type: ignore
        endpoint = validate_endpoint(endpoint)
        # print('*** redis connecting to ', endpoint, flush=True)
        if self._connected:
            raise ConnectionError('Already connected.')
        if not endpoint.startswith('redis://'):
            raise ValueError('Expected endpoint to begin with "redis://".'
                             'Got: {!r}'.format(endpoint))
        host, port = endpoint.replace('redis://', '').split(':')  # todo: handle exception
        self._subscriber = await aioredis.create_redis((host, port))
        self._publisher = await aioredis.create_redis((host, port))
        self._connected = True

    async def _reconnect(self):
        timeout = 100
        while not self._connected and timeout:
            await asyncio.sleep(0.1)
            timeout -= 1
        connection, *_ = await self._subscriber.subscribe(*self._spaces)
        if self._connection:
            self._connection.close()
        if self._listener_task:
            self._listener_task.cancel()
            self._connected = False
        self._connection = connection
        self._listener_task = self._agent.spawn(self._connection_listener())

    def close(self):
        if self._listener_task:
            self._listener_task.cancel()
        if self._connection:
            self._connection.close()
        if self._subscriber:
            self._subscriber.close()
        if self._publisher:
            self._publisher.close()

    async def join(self, space: str) -> None:  # type: ignore

        space = validate_name(space)
        self._spaces.add(space)
        await self._reconnect()

    async def leave(self, space: str) -> None:  # type: ignore
        space = validate_name(space)
        self._spaces.remove(space)
        await self._reconnect()

    def spaces(self):
        return [s for s in self._spaces]

    async def broadcast(self, frame):
        if frame.space:
            spaces = [frame.space]
        else:
            spaces = self._spaces
        for space in spaces:
            await self._publisher.publish_json(space, frame.as_dict())
