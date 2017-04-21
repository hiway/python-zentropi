# coding=utf-8
import asyncio
from typing import Optional

import aioredis
from zentropi import Frame


async def listen(endpoint, spaces):
    host, port = endpoint.replace('redis://', '').split(':')  # todo: handle exception
    subscriber = await aioredis.create_redis((host, port))
    connection, *_ = await subscriber.subscribe(*spaces)
    while await connection.wait_message():
        frame_as_dict = await connection.get_json()
        if not frame_as_dict:
            break
        frame = Frame.from_dict(frame_as_dict)
        print('incoming {source}@{space}: {name} :: {data}'.format(
            name=frame.name,
            data=frame.data,
            space=frame.space,
            source=frame.source))
    print('*** redis disconnected')


loop = asyncio.get_event_loop()
loop.run_until_complete(listen('redis://localhost:6379', ['telegram']))
