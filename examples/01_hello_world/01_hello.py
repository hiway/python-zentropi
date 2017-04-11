# coding=utf-8
from zentropi import Agent

bot = Agent()


@bot.on_event('*** started')
def say_hello(self, event):
    print('Hello, world!')


@bot.on_timer(1)
def every_second():
    print('.')


@bot.on_timer(3)
def bye_bye():
    bot.stop()


bot.run()
