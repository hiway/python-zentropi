# coding=utf-8
from zentropi import on_message
from zentropi import Agent


class MyBot(Agent):
    @on_message('help')
    async def help(self, message):
        return 'Hi, I am an example slack bot. I respond to: help, hello and a few greetings.'

    @on_message('good {time_of_day}', parse=True)
    async def greeting(self, message):
        """
        Matches text pattern "good [time_of_day]"
        Replies only if time_of_day is a known value.
        """
        # Extract field time_of_day from message.data, remove any extra spaces and lower-case it.
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
    from zentropi.contrib.agents import SlackAgent
    from zentropi import run_agents

    slack_agent = SlackAgent()
    my_bot = MyBot('slacker')

    run_agents(slack_agent, my_bot, join='slack', endpoint='inmemory://slack')
