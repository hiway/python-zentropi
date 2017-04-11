# coding=utf-8
from zentropi import Agent
from zentropi import on_event
from zentropi import on_timer


class HelloBot(Agent):
    @on_event('*** started')
    def say_hello(self, event):
        print('Hello, world!')

    @on_timer(1)
    def every_second(self):
        print('.')
        self.stop()


bot = HelloBot()
bot.run()
