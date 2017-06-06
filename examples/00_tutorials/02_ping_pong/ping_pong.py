# coding=utf-8
from zentropi import (
    Agent,
    on_event,
    on_timer,
    run_agents
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
    ping_bot = PingBot(name='ping', auth='3aa84b9b93e944348fad6d5161c6c1f1')
    pong_bot = PongBot(name='pong', auth='14d91609405145999614b3c11ceb4513')
    run_agents(ping_bot, pong_bot, shell=False,
               endpoint='wss://local.zentropi.com/',
               space='zentropia')
