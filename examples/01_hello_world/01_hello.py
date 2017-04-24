# coding=utf-8
from zentropi import Agent
from zentropi import on_message

# Create an instance of Agent.
agent = Agent('hello_bot')


# Trigger on "hello"
@agent.on_message('hello')
def say_hello(message):
    # Send reply to the incoming message.
    return 'Hello, world!'


# Connect to local redis.
agent.connect('redis://localhost:6379')

# Join "test" space.
agent.join('test')

agent.run()
