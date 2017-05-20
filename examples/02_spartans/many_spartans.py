#!/usr/bin/env python
# coding=utf-8

from zentropi import Agent, on_message, run_agents


class Spartan(Agent):
    @on_message('Spartans?', fuzzy=True)
    async def war_cry(self, message):
        return 'Ahoo!'


if __name__ == '__main__':
    warriors = [Spartan(name='Spartan_{}'.format(x)) for x in range(1, 301)]
    run_agents(*warriors, space='Thermopylae', shell=True)
