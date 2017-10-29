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
