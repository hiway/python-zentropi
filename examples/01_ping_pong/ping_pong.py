# coding=utf-8
from zentropi import (
    Agent,
    on_event,
    on_timer,
    run_agents,
    ZentropiShell
)


class PingBot(Agent):
    @on_timer(2)
    def send_ping(self):
        self.emit('ping')
        print('PING')

    @on_event('pong')
    def on_pong(self, event):
        print('PONG')


class PongBot(Agent):
    @on_event('ping')
    async def on_ping(self, event):
        await self.sleep(0.2)
        self.emit('pong')


if __name__ == '__main__':
    ping_bot = PingBot(name='ping_bot')
    pong_bot = PongBot(name='pong_bot')
    run_agents(ping_bot, pong_bot, shell=True)
