# coding=utf-8
import asyncio
# import atexit
import threading

from inspect import isgeneratorfunction
from typing import Optional
from typing import Union

from pybloom_live import ScalableBloomFilter

from .frames import Frame
from .handlers import Handler
from .symbols import KINDS
from .timer import TimerRegistry
from .zentropian import Zentropian
from .zentropian import on_state


class Agent(Zentropian):
    def __init__(self, name=None):
        self.timers = TimerRegistry(callback=self._trigger_frame_handler)
        super().__init__(name=name)
        self.states.should_stop = False
        self.states.running = False
        self.loop = None  # asyncio.get_event_loop()
        self._spawn_on_start = set()
        self._seen_frames = ScalableBloomFilter(
                    mode=ScalableBloomFilter.LARGE_SET_GROWTH, error_rate=0.001)

    @on_state('should_stop')
    def _on_should_stop(self, state):
        if state.data.last is False and state.data.value is True:  # skip double close
            self.close()
        return True

    async def _run_forever(self):
        # atexit.register(self.loop.close)
        if self._spawn_on_start:
            [self.spawn(coro) for coro in self._spawn_on_start]
            self._spawn_on_start = None
        await asyncio.sleep(10)
        self.emit('*** started', internal=True)
        self.timers.start_timers(self.spawn)
        await asyncio.sleep(2)
        while self.states.should_stop is False:
            await asyncio.sleep(1)
        self.emit('*** stopped', internal=True)

    def _set_asyncio_loop(self, loop=None):
        if self.loop and loop:
            raise AssertionError('Agent already has an event loop set.')
        if loop:
            self.loop = loop
        if not self.loop:
            self.loop = asyncio.get_event_loop()

    def _trigger_frame_handler(self, frame: Frame, handler: Handler, internal=False):
        if frame.id in self._seen_frames:
            return
        self._seen_frames.add(frame.id)
        payload = []  # type: list
        if handler.pass_self:
            payload.append(self)
        if handler.kind != KINDS.TIMER:
            payload.append(frame)
        if handler.run_async:
            self.spawn(handler(*payload))
        else:
            return handler(*payload)

    def add_handler(self, handler):
        if handler.kind == KINDS.TIMER:
            self.timers.add_handler(handler.name, handler)
        else:
            super().add_handler(handler)

    def on_timer(self, interval):
        def wrapper(handler):
            name = str(interval)
            handler_obj = Handler(kind=KINDS.TIMER, name=name, handler=handler)
            self.timers.add_handler(name, handler_obj)
            return handler

        return wrapper

    def start(self, loop=None):
        self._set_asyncio_loop(loop)
        self.loop.create_task(self._run_forever())

    def run(self):
        self._set_asyncio_loop()
        self.loop.run_until_complete(self._run_forever())

    def spawn(self, coro):
        if not self.loop:
            # print('No loop defined; coroutine will be executed after attach/start/run.', coro)
            self._spawn_on_start.add(coro)
            return
        return self.loop.create_task(coro)

    @staticmethod
    def spawn_in_thread(func, *args, **kwargs):
        task = threading.Thread(target=func, args=args, kwargs=kwargs)
        task.start()

    def stop(self):
        self.states.should_stop = True
        self.timers.should_stop = True

    def connect(self, endpoint, *, tag='default'):
        retval = super().connect(endpoint, tag=tag)
        if not isgeneratorfunction(retval):
            return
        self.spawn(retval)

    def bind(self, endpoint, *, tag='default'):
        retval = super().bind(endpoint, tag=tag)
        if not isgeneratorfunction(retval):
            return
        self.spawn(retval)

    def join(self, space, *, tags: Optional[Union[list, str]] = None):
        retval = super().join(space, tags=tags)
        if not isgeneratorfunction(retval):
            return
        self.spawn(retval)

    def close(self, *, endpoint: Optional[str] = None, tags: Optional[Union[list, str]] = None):
        """Closes all connections if no endpoint or tags given."""
        if endpoint and tags:
            raise ValueError('Expected either endpoint: {!r} or tags: {!r}.'
                             ''.format(endpoint, tags))
        elif endpoint:
            connections = self._connections.connections_by_endpoint(endpoint)
        elif tags:
            connections = self._connections.connections_by_tags(tags)
        else:
            connections = self._connections.connections
        for connection in connections:
            connection.close()


def on_timer(interval):
    def wrapper(handler):
        name = str(interval)
        handler_obj = Handler(kind=KINDS.TIMER, name=name, handler=handler)
        if hasattr(handler, 'meta'):
            handler.meta.append(handler_obj)
        else:
            handler.meta = [handler_obj, ]
        return handler

    return wrapper
