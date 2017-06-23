# coding=utf-8
from logging import getLogger

import uasyncio as asyncio
import ujson as json
from collections import defaultdict, namedtuple
import uwebsockets.client
import utime as time

logger = getLogger(__name__)


class ZentropiError(Exception):
    @classmethod
    def message(cls, message):
        return cls(0x001, message)

    @classmethod
    def unexpected_type(cls, name: str, value, expected: str):
        return cls(0x101, 'Expected `{}`: {} to be of type: {}.'
                          ''.format(name, repr(value), expected))

    @classmethod
    def unset_value(cls, name: str, value):
        return cls(0x103, 'Expected `{}`: {} to hold a value.'
                          ''.format(name, value))


class Frame(object):
    FRAME = 0
    COMMAND = 1
    EVENT = 2

    @staticmethod
    def inflate(frame):
        _frame = {'kind': 0, 'uuid': None, 'name': None, 'data': {}, 'meta': {}}
        _frame.update(frame)
        return _frame

    @staticmethod
    def deflate(frame):
        return {k: v for k, v in frame.items() if v}

    @staticmethod
    def load(frame: dict):
        kind = frame.get('kind', None)
        if not kind:
            raise ZentropiError.unset_value('kind', kind)
        if kind == Frame.EVENT:
            return Event(**Frame.inflate(frame))
        else:
            raise ZentropiError.message('Malformed frame; `kind` is invalid: {}.'.format(kind))

    @staticmethod
    def load_json(frame: str):
        frame = json.loads(frame)
        return Frame.load(frame)

    @staticmethod
    def dump(frame_obj):
        if isinstance(frame_obj, Event):
            return Frame.deflate({
                'kind': frame_obj.kind,
                'uuid': frame_obj.uuid,
                'name': frame_obj.name,
                'data': frame_obj.data,
                'meta': frame_obj.meta,
            })
        else:
            raise NotImplementedError()

    @staticmethod
    def dump_json(frame_obj):
        frame = Frame.dump(frame_obj)
        return json.dumps(frame)

    @staticmethod
    def event(*, name, data=None, meta=None, uuid=None):
        return Event(uuid=uuid, name=name, data=data, meta=meta, kind=Frame.EVENT)


Event = namedtuple('Event', ['uuid', 'name', 'data', 'meta', 'kind'])


class MicroWebsocketConnection(object):
    def __init__(self):
        self._websocket = None
        self._connected = None
        self._endpoint = None
        self._frame_handler = None

    def _process(self, frame):
        frame = Frame.load(frame)
        if isinstance(frame, Event):
            try:
                self._frame_handler(frame.name, frame)
            except KeyError:
                raise KeyError('Malformed event; no `name` specified'.format())
        else:
            print('*** skipping:', frame)

    async def connect(self, endpoint, frame_handler):
        assert self._connected is None
        assert self._websocket is None
        assert self._endpoint is None
        assert endpoint and isinstance(endpoint, str)
        assert frame_handler and callable(frame_handler)
        self._endpoint = endpoint
        self._frame_handler = frame_handler
        with uwebsockets.client.connect(endpoint) as websocket:
            self._connected = True
            self._websocket = websocket
            print('*** connected:', endpoint)
            self._frame_handler('connected', {})
            while True:
                if self._connected is False:
                    break
                ws_frame = websocket.recv()
                try:
                    frame = json.loads(ws_frame)
                except:
                    raise ValueError('Malformed JSON data in frame: {}'.format(ws_frame))
                if isinstance(frame, dict):
                    self._process(frame)

    def send(self, frame):
        assert self._endpoint
        assert self._websocket
        assert self._connected
        self._websocket.send(json.dumps(frame))

    def close(self):
        assert self._websocket is not None
        assert self._connected is True
        self._connected = False
        self._websocket.close()


class Agent(object):
    def __init__(self):
        self._loop = None
        self._event_handlers = defaultdict(set)
        self._should_stop = False
        self._connection = None
        self._connect_on_start = []

    async def _start(self):
        assert self._loop
        assert self._should_stop is False
        if self._connect_on_start:
            [self.spawn(coro) for coro in self._connect_on_start]
            self._connect_on_start = None
        while self._should_stop is False:
            try:
                await asyncio.sleep(1)
            except KeyboardInterrupt:
                break

    @staticmethod
    def _trigger_handler(handler, payload: dict):
        if not isinstance(payload, dict):
            raise ZentropiError.unexpected_type(
                'payload', payload, 'dict')
        if callable(handler):
            return handler(**payload)
        else:
            raise ZentropiError.unexpected_type(
                'handler', handler, 'callable')

    def add_event_handler(self, name, handler):
        self._event_handlers[name].add(handler)

    def remove_event_handler(self, name, handler):
        self._event_handlers[name].remove(handler)

    def _trigger_event_handler(self, name, event):
        handlers = self._event_handlers[name]
        for handler in handlers:
            self._trigger_handler(handler, payload={'event': event})

    def emit(self, name, data=None):
        event = Frame.event(name=name, data=data or {}, uuid=str(time.ticks_us()), meta={})
        self._trigger_event_handler(name, event)
        self._connection.send(Frame.dump(event))

    def on_event(self, name):
        def wrapper(handler):
            self.add_event_handler(name, handler)
            return handler

        return wrapper

    def connect(self, endpoint, connection_class=None):
        assert self._connection is None
        if not connection_class:
            self._connection = MicroWebsocketConnection()
        else:
            self._connection = connection_class()
        self.spawn(self._connection.connect(endpoint, self._trigger_event_handler))

    def close(self):
        self._connection.close()

    def spawn(self, coro):
        if self._loop:
            self._loop.create_task(coro)
        else:
            self._connect_on_start.append(coro)
            print('No loop defined; coroutine will be executed after attach/start/run.')

    def attach(self, loop):
        assert self._loop is None
        self._loop = loop
        self._loop.create_task(self._start())

    def start(self, loop):
        assert self._loop is None
        self._loop = loop
        self._loop.run_until_complete(self._start())

    def run(self):
        assert self._loop is None
        self._loop = asyncio.get_event_loop()
        self._loop.run_until_complete(self._start())

    def stop(self):
        assert self._should_stop is False
        self._should_stop = True
