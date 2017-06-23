# coding=utf-8
from zentropi import run_agents
from .zentweepy import ZenTweepy


def main():
    zentweepy = ZenTweepy(name='ZenTweepy', auth='6aba32bb654f4d2ba750d9bdbaf2b197')
    run_agents(zentweepy, shell=False, space='zentropia',
               endpoint='ws://local.zentropi.com:8000/')
