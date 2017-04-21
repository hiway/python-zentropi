# coding=utf-8
from zentropi import Agent
from zentropi import on_timer


class Hello(Agent):
    @on_timer(1)
    def every_second(self):
        print('Hello, world!')

    @on_timer(3)
    def on_three_seconds(self):
        self.stop()


agent = Hello()
agent.run()
