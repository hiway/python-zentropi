# coding=utf-8
from zentropi import (
    Agent,
    on_message,
    run_agents,
    ZentropiShell,
)
from zentropi.extra.agents import TelegramAgent


class EchoBot(Agent):
    @on_message('help', fuzzy=True)
    async def help(self, message):
        return 'Hi, I am {}. I echo messages.'.format(self.name)

    @on_message('*')
    async def echo(self, message):
        # This handler will be called for all messages: @on_message('*'),
        # we want to skip any messages sent by our own agent ("Echo: ...")
        if message.source == self.name:
            # quit here if we are the source of the message.
            return
        return 'Echo: {}'.format(message.data.text)


if __name__ == '__main__':
    echo_bot = EchoBot('echo_bot')
    telegram_agent = TelegramAgent('tg')
    shell = ZentropiShell('shell')
    run_agents(echo_bot, telegram_agent, shell)
