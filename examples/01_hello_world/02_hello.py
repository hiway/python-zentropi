# coding=utf-8
from zentropi import Agent
from zentropi import on_event


class HelloBot(Agent):
    @on_event('*** started')
    def say_hello(self, event):
        print('Hello, world!')
        self.stop()


bot = HelloBot()
bot.run()
