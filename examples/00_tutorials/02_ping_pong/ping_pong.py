# coding=utf-8
import time
from zentropi import (
    Agent,
    on_event,
    on_timer,
    run_agents
)


class PingBot(Agent):
    @on_timer(1)
    def send_ping(self):
        self.message('ping', data={'text': time.time()})
        print('PING')

    @on_event('button_press')
    def on_pong(self, event):
        self.emit('got_button_press')
        print('PONG')


class PongBot(Agent):
    @on_event('ping')
    async def on_ping(self, event):
        # await self.sleep(0.2)
        self.emit('pong')


if __name__ == '__main__':
    ping_bot = PingBot(name='ping', auth='9ce7cf58fe28425192541d68e77a09e0')
    pong_bot = PongBot(name='pong', auth='1a138eb3533b40bd8afeaa9a909f790e')
    run_agents(ping_bot, pong_bot, shell=False,
               endpoint='wss://trials.zentropi.com/',
               space='zentropia')
