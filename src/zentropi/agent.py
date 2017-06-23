# coding=utf-8
import asyncio
# import atexit
import signal
import threading
import traceback
from inspect import isgeneratorfunction
from typing import Optional, Union

from pybloom_live import ScalableBloomFilter

from zentropi.frames import Event, Frame, Message
from zentropi.handlers import Handler
from zentropi.symbols import KINDS
from zentropi.timer import TimerRegistry
from zentropi.utils import logger
from zentropi.zentropian import (
    Zentropian,
    on_event,
    on_message,
    on_state,
    wrap_handler,
)


class Agent(Zentropian):
    """
    A Zentropian Agent, if you are new to Zentropi, this is where you want to start exploring.

    >>> from zentropi import Agent
    >>>
    >>> agent = Agent(name='hello')
    >>>
    >>> @agent.on_event('*** started')
    >>> def on_started(event):
    >>>     print('hello, world.')
    >>>     agent.stop()
    >>>
    >>> agent.run()
    None
    """

    def __init__(self, name=None, auth=None):
        """
        >>> from zentropi import Agent
        >>>
        >>> agent = Agent(name='hello')
        >>>
        >>> class MyAgent(Agent):
        >>>     pass

        :param name: Name of Agent. Unicode string. Length must be < FRAME_NAME_MAX_LENGTH (default: 128) characters.
        :type name: str
        """
        self.timers = TimerRegistry(callback=self._trigger_frame_handler)
        super().__init__(name=name, auth=auth)
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
        self.emit('*** start', internal=True)
        self.timers.start_timers(self.spawn)
        while self.states.should_stop is False:
            await asyncio.sleep(1)
        self.emit('*** stopped', internal=True)

    def _set_asyncio_loop(self, loop=None):
        if self.loop and loop:
            raise AssertionError('Agent already has an event loop set.')
        if loop:
            self.loop = loop
        if not self.loop:
            try:
                self.loop = asyncio.get_event_loop()
            except RuntimeError:
                self.loop = asyncio.new_event_loop()

    def _trigger_frame_handler(self, frame: Frame, handler: Handler, internal=False):
        if isinstance(frame, Message) and frame.source == self.name:
            return
        if isinstance(frame, Event) and frame.source != self.name and frame.name.startswith('***'):
            return
        if frame and frame.id in self._seen_frames:
            return
        if not self.apply_filters([handler]):
            return
        if frame:
            self._seen_frames.add(frame.id)
        payload = []  # type: list
        if handler.pass_self:
            payload.append(self)
        if handler.kind != KINDS.TIMER:
            payload.append(frame)
        if handler.run_async:
            async def return_handler():
                try:
                    ret_val = await handler(*payload)
                    if ret_val:
                        self.handle_return(frame, return_value=ret_val)
                except Exception as e:
                    # todo: make any exception stop all agents in a process;
                    # todo: send signal/ put exception in a queue?
                    traceback.print_exc()
                    signal.alarm(1)
                    self.stop()
            self.spawn(return_handler())
        else:
            ret_val = handler(*payload)
            if ret_val:
                return self.handle_return(frame, return_value=ret_val)

    def add_handler(self, handler):
        if handler.kind == KINDS.TIMER:
            self.timers.add_handler(handler.name, handler)
        else:
            super().add_handler(handler)

    def on_timer(self, interval, **kwargs):
        def wrapper(handler):
            name = str(interval)
            handler_obj = wrap_handler(kind=KINDS.TIMER, name=name, handler=handler, **kwargs)
            self.timers.add_handler(name, handler_obj)
            return handler

        return wrapper

    @staticmethod
    def sleep(duration: float):
        return asyncio.sleep(duration)

    def start(self, loop=None):
        self._set_asyncio_loop(loop)
        self.loop.create_task(self._run_forever())

    def run(self):
        self._set_asyncio_loop()
        self.loop.run_until_complete(self._run_forever())

    def spawn(self, coro):
        if not self.loop:
            self._spawn_on_start.add(coro)
            return
        return self.loop.create_task(coro)

    @staticmethod
    def spawn_in_thread(func, daemon=True, *args, **kwargs):
        task = threading.Thread(target=func, args=args, kwargs=kwargs, daemon=daemon)
        task.start()
        return task

    def run_in_thread(self, func=None, daemon=True, *args, **kwargs):
        return self.spawn_in_thread(func or self.run,  daemon=True, *args, **kwargs)

    def stop(self):
        self.emit('*** stop', internal=True)
        logger.debug('{} emitted shutdown signal'.format(type(self).__name__))
        self.states.should_stop = True
        self.timers.should_stop = True

    def connect(self, endpoint, *, auth=None, tag='default'):
        retval = super().connect(endpoint, auth=auth, tag=tag)
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

    def leave(self, space, *, tags: Optional[Union[list, str]] = None):
        retval = super().leave(space, tags=tags)
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

    def describe(self):
        description = {
            'name': self.name,
            'help': self.__doc__,
            'events': self.events.describe(),
            'messages': self.messages.describe(),
            'states': self.states.describe(),
            'timers': self.timers.describe(),
        }
        from .utils import deflate_dict
        return deflate_dict(description)


def on_timer(interval, **kwargs):
    def wrapper(handler):
        name = str(interval)
        wrap_handler(kind=KINDS.TIMER, name=name, handler=handler, **kwargs)
        return handler

    return wrapper


__all__ = [
    'Agent',
    'on_event',
    'on_message',
    'on_state',
    'on_timer',
]
