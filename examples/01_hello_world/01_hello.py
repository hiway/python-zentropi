# coding=utf-8
from zentropi import Agent

bot = Agent()


@bot.on_event('*** started')
def say_hello(self, event):
    print('Hello, world!')
    bot.stop()


bot.run()
