# coding=utf-8
import asyncio
import threading

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
        self._loop = None

    @on_state('should_stop')
    def _on_should_stop(self, state):
        if state.data.last is False and state.data.value is True:  # skip double close
            self.close()
        return True

    async def _run_forever(self):
        self.emit('*** started', internal=True)
        self.timers.start_timers(self.spawn)
        while self.states.should_stop is False:
            await asyncio.sleep(1)
        self.emit('*** stopped', internal=True)

    def _set_asyncio_loop(self, loop=None):
        if self._loop and loop:
            raise AssertionError('Agent already has an event loop set.')
        if loop:
            self._loop = loop
        if not self._loop:
            self._loop = asyncio.get_event_loop()

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
        self._loop.create_task(self._run_forever())

    def run(self):
        self._set_asyncio_loop()
        self._loop.run_until_complete(self._run_forever())

    def spawn(self, coro):
        return self._loop.create_task(coro)

    @staticmethod
    def spawn_in_thread(func, *args, **kwargs):
        task = threading.Thread(target=func, args=args, kwargs=kwargs)
        task.start()

    def stop(self):
        self.states.should_stop = True
        self.timers.should_stop = True


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
