#!/usr/bin/env python
# coding=utf-8

from zentropi import (
    Agent,
    on_message,
    run_agents
)


class Spartan(Agent):
    @on_message('Spartans?', fuzzy=True)
    def war_cry(self, message):
        return 'Ahoo!'


if __name__ == '__main__':
    from zentropi.shell import ZentropiShell
    shell = ZentropiShell('shell')
    warrior = Spartan(name='Spartan')
    run_agents(shell, warrior, space='Thermopylae')
