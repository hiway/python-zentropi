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
from zentropi.api import API
from uzentropi.utils import save_token, load_token, TOKENS_PATH

DEFAULT_CHOICE_NOTE = """
Not what you want? Press Ctrl+C to cancel. See available choices by:
$ zentropi {} --help
"""


def get_api():
    # token = os.getenv('ZENTROPI_API_TOKEN', '')
    try:
        token = load_token('user:default')
    except KeyError:
        token = None
    return API(endpoint='https://zentropi.com/api', token=token)


@click.group()
def cli():
    pass


@cli.command()
def register():
    api = get_api()
    username = click.prompt('username')
    email = click.prompt('email')
    password = click.prompt('password', hide_input=True)
    click.echo(api.register(email, username, password))


@cli.command()
def login():
    api = get_api()
    username = click.prompt('username')
    password = click.prompt('password', hide_input=True)
    token = api.login(username, password)
    if isinstance(token, dict):
        click.echo('Invalid username or password.')
        raise click.Abort()
    save_token('user:default', token)
    click.echo('Your user-token is saved to {}'.format(TOKENS_PATH))


@cli.command()
@click.argument('agent_name')
def login_agent(agent_name):
    api = get_api()
    agent_token = api.login_agent(agent_name)
    if isinstance(agent_token, dict):
        click.echo('Invalid agent name.')
        raise click.Abort()
    save_token(agent_name, agent_token)
    click.echo('Token for agent {} is saved to {}'.format(agent_name, TOKENS_PATH))


@cli.group()
def create():
    pass


@create.command()
@click.argument('path', type=click.Path(exists=False), default='.')
@click.option('--template', default='package')
def project(path, template):
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
@click.argument('name')
@click.argument('description', default='')
@click.option('--login', is_flag=True, default=False)
@click.option('--spaces', default='')
def agent(name, description, login, spaces):
    api = get_api()
    click.echo('Creating agent {}...'.format(name))
    click.echo(api.agent_create(name, description))
    click.echo('{} created.'.format(name))
    if spaces:
        for space in spaces.split(','):
            click.echo('Joining {}'.format(space))
            click.echo(api.join(space, name))
    if login:
        click.echo('Logging in...')
        agent_token = api.login_agent(name)
        if isinstance(agent_token, dict):
            click.echo('Invalid agent name.')
            raise click.Abort()
        save_token(name, agent_token)
        click.echo('Token for agent {} is saved to {}'.format(name, TOKENS_PATH))


@create.command()
@click.argument('name')
@click.argument('description', default='')
def space(name, description):
    api = get_api()
    click.echo(api.space_create(name, description))


@cli.command()
@click.argument('space')
@click.argument('agent')
def join(space, agent):
    api = get_api()
    click.echo(api.join(space, agent))


@cli.command()
@click.argument('space')
@click.argument('agent')
def leave(space, agent):
    api = get_api()
    click.echo(api.leave(space, agent))


@cli.command()
@click.argument('space', default='all')
def agents(space):
    api = get_api()
    if space == 'all':
        all_agents = api.all_agents()
        if not isinstance(all_agents, list):
            click.echo(all_agents)
        else:
            click.echo([a['name'] for a in all_agents])
    else:
        click.echo(api.agents(space))


@cli.command()
@click.argument('agent', default='all')
def spaces(agent):
    api = get_api()
    if agent == 'all':
        all_spaces = api.all_spaces()
        if not isinstance(all_spaces, list):
            click.echo(all_spaces)
        else:
            click.echo([s['name'] for s in all_spaces])
    else:
        click.echo(api.spaces(agent))


@cli.command()
def shell():
    from .shell import ZentropiShell
    token = ''
    shell = ZentropiShell()
    shell.run('wss://zentropi.com/zensocket', token)
