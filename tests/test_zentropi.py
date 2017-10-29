# coding=utf-8
import sys
import unittest

try:  # pragma: no cover
    import os

    sys.path.append(os.path.join(
        os.path.dirname(__file__),
        '..', 'src',
    ))
    ZENSOCKET_TEST_TOKEN = os.getenv('ZENSOCKET_TEST_TOKEN')
except ImportError:  # pragma: no cover
    ZENSOCKET_TEST_TOKEN = sys.argv[1]

assert ZENSOCKET_TEST_TOKEN, 'Set ZENSOCKET_TEST_TOKEN or pass as argument, cannot proceed if empty.'

try:
    import json
    import asyncio
    import time
except ImportError:  # pragma: no cover
    import ujson as json
    import asyncio_priority as asyncio
    import utime as time

from zentropi import (
    Frame,
    Handler,
    Kind,
    Session,
    RateLimitError,
    WebsocketConnection,
)
from zentropi.errors import async_rate_limit_error

frame_as_dict = {'kind': Kind.EVENT, 'name': 'hello', 'data': {'a': 1}, 'meta': {'source': 'test_source'}}


class TestUZentropi(unittest.TestCase):
    def test_exceptions(self):
        e = RateLimitError()
        self.assertTrue(isinstance(e, Exception))

    def test_async_rate_limit_error(self):
        async def test_arle():
            e = await async_rate_limit_error(name='test')
            self.assertTrue(isinstance(e, Exception))

        asyncio.get_event_loop().run_until_complete(test_arle())

    def test_kind(self):
        self.assertEqual(Kind.TIMER, -1)
        self.assertEqual(Kind.COMMAND, 1)
        self.assertEqual(Kind.EVENT, 2)
        self.assertEqual(Kind.MESSAGE, 3)
        self.assertEqual(Kind.REQUEST, 4)
        self.assertEqual(Kind.RESPONSE, 5)
        self.assertEqual(Kind.STATE, 6)

    def test_frame(self):
        frame = Frame.from_dict(frame_as_dict)
        self.assertEqual(frame.kind, Kind.EVENT)
        self.assertEqual(frame.name, 'hello')
        self.assertEqual(frame.data, {'a': 1})
        self.assertEqual(frame.get_data('a'), 1)
        self.assertEqual(frame.get_meta('source'), 'test_source')

        self.assertEqual(frame.as_dict(), frame_as_dict)
        self.assertEqual(json.loads(frame.as_json()), frame_as_dict)

        frame_from_json = frame.from_json(frame.as_json())
        self.assertEqual(frame_from_json.as_dict(), frame_as_dict)

        frame_copy = frame.copy()
        self.assertEqual(frame_copy.name, frame.name)
        self.assertEqual(frame_copy.kind, frame.kind)
        self.assertEqual(frame_copy.data, frame.data)
        self.assertEqual(frame_copy.meta, frame.meta)

        frame_as_dict.update({'unknown': 'key'})
        safe_frame = Frame.from_dict(frame_as_dict)
        self.assertEqual(safe_frame.name, frame.name)
        self.assertEqual(safe_frame.kind, frame.kind)
        with self.assertRaises(AttributeError):
            safe_frame.unknown
        with self.assertRaises(TypeError):
            Frame(**frame_as_dict)
        del frame_as_dict['unknown']

    def test_session_recv(self):
        session = Session()
        frame, send = session.recv(frame_as_dict)
        self.assertEqual(send, None)
        self.assertEqual(frame.name, 'hello')
        self.assertEqual(frame.data, {'a': 1})
        self.assertEqual(frame.get_data('a'), 1)
        self.assertEqual(frame.get_meta('source'), 'test_source')

    def test_session_send(self):
        session = Session()
        recv, frame = session.send(Kind.EVENT,
                                   name='hello',
                                   data={'a': 1},
                                   meta={'source': 'test_source'},
                                   )
        self.assertEqual(recv, None)
        self.assertEqual(frame.name, 'hello')
        self.assertEqual(frame.data, {'a': 1})
        self.assertEqual(frame.get_data('a'), 1)
        self.assertEqual(frame.get_meta('source'), 'test_source')

        # without meta
        recv, frame = session.send(Kind.EVENT,
                                   name='hello',
                                   data={'a': 1},
                                   )
        self.assertEqual(recv, None)
        self.assertEqual(frame.name, 'hello')
        self.assertEqual(frame.data, {'a': 1})
        self.assertEqual(frame.get_data('a'), 1)
        self.assertEqual(frame.get_meta('source'), None)

        recv, frame = session.send(Kind.EVENT, space='test_space')
        self.assertEqual(frame.get_meta('space'), 'test_space')

        recv, frame = session.send(Kind.EVENT, target='test_target')
        self.assertEqual(frame.get_meta('target'), 'test_target')

        recv, frame = session.send(Kind.EVENT, reply_to='test_id')
        self.assertEqual(frame.get_meta('reply_to'), 'test_id')

    def test_handler(self):
        async def _test(agent):
            self.assertTrue(agent)

        handler = Handler(Kind.EVENT, 'test_name', _test, rate_limit=0.1)
        self.assertEqual(handler.name, 'test_name')
        self.assertEqual(handler.kind, Kind.EVENT)
        self.assertEqual(handler._callable, _test)
        asyncio.get_event_loop().run_until_complete(handler(True))
        time.sleep(0.12)
        asyncio.get_event_loop().run_until_complete(handler(True))

        async def verify_error():
            r = await handler(True)
            self.assertTrue(isinstance(r, RateLimitError))
            raise r

        with self.assertRaises(RateLimitError):
            asyncio.get_event_loop().run_until_complete(verify_error())
        self.assertEqual(handler.call_total, 3)
        self.assertEqual(handler.describe(),
                         {
                             'kind': Kind.EVENT,
                             'name': 'test_name',
                             'expects': None,
                         })

    def test_websocket(self):
        ws = WebsocketConnection()
        asyncio.get_event_loop().run_until_complete(
            ws.send(Kind.EVENT, name='test'))
        self.assertTrue(True)
        asyncio.get_event_loop().run_until_complete(
            ws.send_frame(frame_as_dict))
        self.assertTrue(True)

    def test_websocket_connection(self):
        ws = WebsocketConnection()
        asyncio.get_event_loop().run_until_complete(
            ws.connect('ws://192.168.1.3:8080/zensocket', ZENSOCKET_TEST_TOKEN)
        )

        async def test_recv(frame):
            self.assertEqual(frame.name, 'test')
            await ws.close()
            asyncio.get_event_loop().stop()

        async def test_send():
            await asyncio.sleep(0.1)
            await ws.send(Kind.EVENT, name='test')

        asyncio.get_event_loop().create_task(ws.listen(test_recv))
        asyncio.get_event_loop().create_task(test_send())
        asyncio.get_event_loop().run_forever()


if __name__ == '__main__':  # pragma: no cover
    unittest.main()
