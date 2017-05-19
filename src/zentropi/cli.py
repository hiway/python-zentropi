# coding=utf-8
"""
Module that contains the command line app.

Why does this file exist, and why not put this in __main__?

  You might be tempted to import things from __main__ later, but that will cause
  problems: the code will get executed twice:

  - When you run `python -mzentropi` python will execute
    ``__main__.py`` as a script. That means there won't be any
    ``zentropi.__main__`` in ``sys.modules``.
  - When you import __main__ it will get executed again (as a module) because
    there's no ``zentropi.__main__`` in ``sys.modules``.

  Also see (1) from http://click.pocoo.org/5/setuptools/#setuptools-integration
"""
import click
import os


@click.group()
def main():
    pass


@main.command()
@click.option('--name', default='zentropi_shell')
@click.option('--endpoint', default='redis://127.0.0.1:6379')
@click.option('--auth/--no-auth', 'send_auth', is_flag=True, default=True)
@click.option('--join', default='zentropia')
def shell(name, endpoint, join, send_auth):
    from .shell import ZentropiShell
    if send_auth:
        auth = os.getenv('ZENTROPI_REDIS_PASSWORD', None)
    else:
        auth = None
    shell_agent = ZentropiShell(name)
    shell_agent.connect(endpoint, auth=auth)
    if join:
        shell_agent.join(space=join)
    shell_agent.run()
