# coding=utf-8

from zentropi import (
    Agent,
    ZentropiShell,
    on_message,
    run_agents
)


class HelloBot(Agent):
    @on_message('hello')
    def say_hello(self, message):
        return 'hello, world'


if __name__ == '__main__':
    hello_bot = HelloBot(name='hello_bot')
    shell = ZentropiShell(name='shell')
    run_agents(hello_bot, shell)
