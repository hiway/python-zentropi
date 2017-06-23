# coding=utf-8
import logging


from zentropi import (
    Agent,
    on_message,
    run_agents,
    log_to_stream
)

logger = log_to_stream(enable=True)


class HelloBot(Agent):
    @on_message('hello')
    def say_hello(self, message):
        self.emit('esp_gpio_on', data={'pin': 13})
        return 'hello, world'


if __name__ == '__main__':
    hello_bot = HelloBot(name='hello_bot', auth='462961d4b6194a5fbab168d3e330a158')
    run_agents(hello_bot, shell=True, endpoint='ws://127.0.0.1:8000/')
