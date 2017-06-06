# coding=utf-8
import logging


from zentropi import (
    Agent,
    on_message,
    run_agents,
)


class HelloBot(Agent):
    @on_message('hello')
    def say_hello(self, message):
        return 'hello, world'


if __name__ == '__main__':
    hello_bot = HelloBot(name='hello_bot')
    run_agents(hello_bot, shell=True)
