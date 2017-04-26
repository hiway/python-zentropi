# coding=utf-8
import asyncio

from zentropi.contrib.agents import SlackAgent
from zentropi import on_event
from zentropi import on_message
from zentropi import Agent


class MySlackAgent(Agent):
    @on_message('help')
    async def help(self, message):
        return 'Hi, I am an example slack bot. I respond to: help, hello and a few greetings.'

    @on_message('good {timeofday}', parse=True)
    async def greeting(self, message):
        if message.source == self.name:
            return
        timeofday = message.data.timeofday.strip().lower()
        if timeofday == 'morning':
            return 'Top of the morning to you!'
        elif timeofday in ['afternoon', 'evening', 'night']:
            return 'Good {}!'.format(timeofday)


if __name__ == '__main__':
    slack_agent = SlackAgent()
    slack_agent.bind('inmemory://slack')
    slack_agent.join('slack')

    agent = MySlackAgent('slacker')
    agent.connect('inmemory://slack')
    agent.join('slack')

    slack_agent.start()
    agent.loop = slack_agent.loop
    agent.run()
