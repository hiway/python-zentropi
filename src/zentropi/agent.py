import asyncio

from uzentropi import Agent as uAgent, RATE_LIMIT, Kind, Frame, MICROPY, PLATFORM
from uzentropi.agent import wrap_handler
from uzentropi.utils import random_id


def on_command(_name: str, rate_limit=RATE_LIMIT, **expects):
    def wrapper(func):
        return wrap_handler(Kind.COMMAND, _name, func, expects, rate_limit=rate_limit)

    return wrapper


class Agent(uAgent):
    async def command(self, _name, space='', broadcast=True, internal=False, **kwargs):
        frame = Frame(Kind.COMMAND, id=random_id(), name=_name, data=kwargs, meta={'source': self.name, 'space': space})
        try:
            return await self.send_frame(frame, broadcast, internal)
        except Exception as e:
            if PLATFORM is MICROPY:
                return
            import traceback
            traceback.print_exc()

    def spawn_in_thread(self, func, *args, wait=True, **kwargs):
        import threading
        queue = asyncio.Queue(maxsize=1)

        def task_wrapper(*args, **kwargs):
            try:
                retval = func(*args, **kwargs)
            except Exception as e:
                retval = e
            finally:
                if not wait:
                    return
                self._loop.create_task(queue.put(retval))

        task = threading.Thread(target=task_wrapper, args=args, kwargs=kwargs)
        task.start()
        if wait:
            async def wait_for_task():
                retval = await queue.get()
                if not isinstance(retval, Exception):
                    return retval
                raise retval

            return wait_for_task()
        return task

    def attach(self, loop, endpoint=None, token=None):
        assert not self._loop, 'event loop already initialized, call attach() instead of -> start() or run()'
        self._loop.create_task(self.start(endpoint=endpoint, token=token, loop=loop))
