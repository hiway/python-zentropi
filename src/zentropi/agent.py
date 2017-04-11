# coding=utf-8
import asyncio

from .zentropian import Zentropian
from .zentropian import on_state


class Agent(Zentropian):
    def __init__(self, name=None):
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

    def start(self, loop=None):
        self._set_asyncio_loop(loop)
        self._loop.create_task(self._run_forever())

    def run(self):
        self._set_asyncio_loop()
        self._loop.run_until_complete(self._run_forever())

    def stop(self):
        self.states.should_stop = True
