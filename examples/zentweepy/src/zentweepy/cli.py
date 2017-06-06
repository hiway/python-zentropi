# coding=utf-8
from zentropi import run_agents
from .zentweepy import ZenTweepy


def main():
    zentweepy = ZenTweepy(name='ZenTweepy', auth='c0eddc73d5c747ed8478bb25f7aee7d6')
    run_agents(zentweepy, shell=False, space='zentropia',
               endpoint='wss://zentropi.com/')
