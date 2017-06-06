# coding=utf-8
from zentropi import run_agents
from .zentinker import ZenTinKer


def main():
    zentinker = ZenTinKer(name='ZenTinKer')
    run_agents(zentinker, shell=False)
