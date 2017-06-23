# coding=utf-8
from zentropi import run_agents
from .zenbrowser import Zenbrowser


def main():
    zenbrowser = Zenbrowser(name='Zenbrowser')
    run_agents(zenbrowser, shell=True, endpoint='redis://127.0.0.1:6379')
