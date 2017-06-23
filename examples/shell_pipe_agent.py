#!/usr/bin/env python
# coding=utf-8

import asyncio
import sys
from asyncio.streams import FlowControlMixin, StreamWriter
import time

import os

from zentropi import Agent

reader, writer = None, None


async def stdio(loop=None):
    if loop is None:
        loop = asyncio.get_event_loop()

    reader = asyncio.StreamReader()
    reader_protocol = asyncio.StreamReaderProtocol(reader)

    writer_transport, writer_protocol = await loop.connect_write_pipe(FlowControlMixin, os.fdopen(1, 'wb'))
    writer = StreamWriter(writer_transport, writer_protocol, None, loop)

    await loop.connect_read_pipe(lambda: reader_protocol, sys.stdin)

    return reader, writer


async def async_input(message):
    """https://gist.github.com/nathan-hoad/8966377"""
    if isinstance(message, str):
        message = message.encode('utf8')

    global reader, writer
    if (reader, writer) == (None, None):
        reader, writer = await stdio()

    # writer.write(message)
    # await writer.drain()

    line = await reader.readline()
    return line.decode('utf8').replace('\r', '').replace('\n', '')


pipe = Agent('pipe')

pipe.connect('ws://127.0.0.1:8000/', auth='6aba32bb654f4d2ba750d9bdbaf2b197')
pipe.join('zentropia')


@pipe.on_event('*** start')
async def stuff(event):
    counter = 0
    last_line = ''
    last_sent = time.time()
    while True:
        line = await async_input(None)
        counter += 1
        if line.strip():
            last_line = line.strip()
        if not line:
            break
        if counter < 3 or ((counter % 10) == 0):
            print('***', line)
            pipe.message(line)
            last_sent = time.time()
            continue
        elif last_sent > (time.time() + 1000):
            print('***', line)
            pipe.message(line)
            last_sent = time.time()
            continue
    if last_line:
        pipe.message(last_line)
        print('***', last_line)
        await asyncio.sleep(1)
    pipe.stop()
    await asyncio.sleep(1)


pipe.run()
