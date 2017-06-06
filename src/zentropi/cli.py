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
import os

import click

from cookiecutter.main import cookiecutter

DEFAULT_CHOICE_NOTE = """
Not what you want? Press Ctrl+C to cancel. See available choices by:
$ zentropi {} --help
"""


@click.group()
def main():
    pass


@main.command()
@click.option('--name', default='zentropi_shell')
@click.option('--endpoint', default='wss://local.zentropi.com/')
@click.option('--auth', default='4cb1c5fe714b469caae03f26e635f676')
@click.option('--join', default='zentropia')
def shell(name, endpoint, join, auth):
    from .shell import ZentropiShell
    shell_agent = ZentropiShell(name)
    shell_agent.connect(endpoint, auth=auth)
    if join:
        shell_agent.join(space=join)
    shell_agent.run()


@main.group()
def create():
    pass


@create.command()
@click.argument('path', type=click.Path(exists=False), default='.')
@click.option('--template', default='package')
def agent(path, template):
    """
    Create a new agent.
    - Default path '.' will create a new directory inside your
        current working directory.
    - Default template 'package' will create a new agent that can
        be installed as a package with pip. You can pick either:
            - package: default, pip-install and pypi ready package.
            - module: one module with multiple files.
            - file: a single python file
            - tutorial: a zentropi tutorial
    """
    if template == 'agent':
        click.echo('Chosen options')
        click.echo('\t--template={}'.format(template))
        click.echo(DEFAULT_CHOICE_NOTE.format('agent create'))
    if any([patrn in template for patrn in ['gh:', 'github', 'bitbucket']]):
        template_path = template
    elif '/' in template:  # points to a path on the filesystem
        template_path = os.path.abspath(template)
    else:
        template_dir = os.path.join(os.path.dirname(__file__), 'templates/')
        template_path = os.path.join(template_dir, template)

    cookiecutter(template_path, output_dir=path)


@create.command()
def project():
    pass
