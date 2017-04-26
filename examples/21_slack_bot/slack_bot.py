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

    @on_message('good {time_of_day}', parse=True)
    async def greeting(self, message):
        """
        Matches text pattern "good [time_of_day]"
        Replies only if time_of_day is a known value.
        """
        if message.source == self.name:
            # We don't want to trigger on our own messages;
            # useful elsewhere, but will put us in a loop
            # if we reply to 'good morning' with 'good morning!'.
            # instead, if we are the source of the message, skip.
            return

        # Extract the parsed field (time_of_day) from message.data, remove any extra spaces and lower-case it.
        time_of_day = message.data.time_of_day.strip().lower()

        # Make a decision
        if time_of_day == 'morning':
            # Returning a string will send a reply to the appropriate channel.
            return 'Top of the morning to you!'
        elif time_of_day in ['afternoon', 'evening', 'night']:
            return 'Good {}!'.format(time_of_day)
        # For "Good [whatever]", we won't respond.
        return


if __name__ == '__main__':
    # Execute the following only if run as a script.

    # Make an instance of SlackAgent and bind it to `inmemory://slack`
    # Also join a space, so the two agents can communicate.
    slack_agent = SlackAgent()
    slack_agent.bind('inmemory://slack')
    slack_agent.join('slack')

    # Make an instance of our custom agent that interacts with SlackAgent
    # to build our Slack bot, connect and join same as slack_agent.
    agent = MySlackAgent('slacker')
    agent.connect('inmemory://slack')
    agent.join('slack')

    # Start the first agent, which will create an asyncio event loop
    slack_agent.start()

    # Use the loop from first agent to initialize other agents...
    # another_agent.start(slack_agent.loop)

    # The last agent will run with all other agents, give it the
    # event loop and run()!
    agent.loop = slack_agent.loop
    agent.run()
