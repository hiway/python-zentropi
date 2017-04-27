# coding=utf-8
import asyncio

from zentropi.handlers import Registry


class TimerRegistry(Registry):
    def __init__(self, callback=None):
        super().__init__(callback=callback)
        self.should_stop = False

    def start_timers(self, spawn_func):
        for interval, handlers in self._registry._handlers.items():
            for handler in handlers:
                spawn_func(self._timer_wrapper(handler))

    async def _timer_wrapper(self, handler) -> None:
        while True:
            await asyncio.sleep(float(handler.name))
            if self.should_stop:
                break
            self.callback(frame=None, handler=handler)
