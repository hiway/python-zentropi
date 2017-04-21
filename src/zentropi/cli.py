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


@click.group()
def main():
    pass


@main.command()
@click.option('--name', default='zentropi_shell')
@click.option('--endpoint', default='redis://localhost:6379')
@click.option('--join', default='')
def shell(name, endpoint, join):
    from .shell import ZentropiShell
    shell_agent = ZentropiShell(name)
    shell_agent.connect(endpoint)
    if join:
        shell_agent.join(space=join)
    shell_agent.run()
