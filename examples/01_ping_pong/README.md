# ping-pong

We said hello to our first minion `HelloBot` in the previous example.
In ping-pong, we will explore how Zentropi can be used for async
machine-to-machine communication.

We will create two agents for this example -

1. PingBot that periodically sends out an `event`
    named `'ping'` and waits for another `event`
    named `pong`.
2. PongBot that waits for `event` named `ping`,
    and, as you have guessed, sends out `pong`

Here is how we can implement them:

```python
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
    shell = ZentropiShell(name='shell')
    run_agents(ping_bot, pong_bot, shell)
```
