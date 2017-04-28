# coding=utf-8
from zentropi.shell import ZentropiShell
from zentropi import (
    Agent,
    on_message,
    run_agents
)


class HelloBot(Agent):
    @on_message('hello', fuzzy=True)
    def on_hello(self, message):
        return 'Hi!'


hello_bot = HelloBot()
shell = ZentropiShell()
run_agents(shell, hello_bot, join='slack', endpoint='inmemory://test')
