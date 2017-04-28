========
Overview
========

.. start-badges

.. list-table::
    :stub-columns: 1

    * - docs
      - |docs|
    * - tests
      - | |travis| |requires|
        |
    * - package
      - | |license| |version| |wheel| |supported_versions| |supported_implementations|
        | |commits_since|

.. |docs| image:: https://readthedocs.org/projects/zentropi/badge/?style=flat
    :target: https://readthedocs.org/projects/zentropi
    :alt: Documentation Status

.. |travis| image:: https://travis-ci.org/zentropi/python-zentropi.svg?branch=master
    :alt: Travis-CI Build Status
    :target: https://travis-ci.org/zentropi/python-zentropi

.. |requires| image:: https://requires.io/github/zentropi/python-zentropi/requirements.svg?branch=master
    :alt: Requirements Status
    :target: https://requires.io/github/zentropi/python-zentropi/requirements/?branch=master

.. |version| image:: https://img.shields.io/pypi/v/zentropi.svg
    :alt: PyPI Package latest release
    :target: https://pypi.python.org/pypi/zentropi

.. |commits_since| image:: https://img.shields.io/github/commits-since/zentropi/python-zentropi/v0.1.2.svg
    :alt: Commits since latest release
    :target: https://github.com/zentropi/python-zentropi/compare/v0.1.2...master

.. |wheel| image:: https://img.shields.io/pypi/wheel/zentropi.svg
    :alt: PyPI Wheel
    :target: https://pypi.python.org/pypi/zentropi

.. |supported_versions| image:: https://img.shields.io/pypi/pyversions/zentropi.svg
    :alt: Supported versions
    :target: https://pypi.python.org/pypi/zentropi

.. |supported_implementations| image:: https://img.shields.io/pypi/implementation/zentropi.svg
    :alt: Supported implementations
    :target: https://pypi.python.org/pypi/zentropi

.. |license| image:: https://img.shields.io/badge/license-Apache%202-blue.svg
    :target: https://raw.githubusercontent.com/zentropi/python-zentropi/master/LICENSE

.. end-badges

Zentropi: Script Your World.
============================

Zentropi is for you if:

- You like the idea of making your own bots.
- You want to build your personal internet-of-things.
- You are curious about automation at work and/or home.
- You care about your time; automation lets you do more of things you enjoy.
- You consider building your own tools to tackle the increasing complexity of your responsibilities.
- You imagine a world where your real and virtual worlds can interact with each other seamlessly.
- You dream of raising your own army of minions... doing your work tirelessly while you take a vaca...

..where were we? Ah, yes, if any of these ^^ sound familiar, you are not alone!

Zentropi makes it easier to write agents that can communicate with each other using
concepts such as State, Event and Message, each is implemented as a simple to learn
and easy to use API.


Installation
============

::

    pip install zentropi

Documentation
=============

https://zentropi.readthedocs.io/


Example
=======

Let us make an agent that will reply to a "hello" message with "Hello, world!"

::

    # coding=utf-8
    from zentropi.shell import ZentropiShell
    from zentropi import (
        Agent,
        on_message,
        run_agents
    )


    class HelloBot(Agent):
        @on_message('hello')
        def on_hello(self, message):
            return 'Hi!'


    hello_bot = HelloBot('hello_bot')
    shell = ZentropiShell('shell')
    run_agents(shell, hello_bot, join='test_space', endpoint='inmemory://test')


Save this as "hello.py"

Let us run it using the command:
::

    $ python hello.py


We can now interact with our newly created agent using our built-in shell prompt.
While starting up, the shell itself emits events, which you can see displayed
on the screen as ``⚡ ︎ @shell: 'shell-starting'`` followed by ``⚡ ︎ @shell: 'shell-ready'``.

You will be presented with a prompt ``〉``, where you can type in messages to be broadcast
to all the spaces that the shell has joined. Go ahead and type "hello", followed by ENTER key.

::

    $ python hello.py
    ⚡ ︎ @shell: 'shell-starting'
    ⚡ ︎ @shell: 'shell-ready'
    〉hello
    ✉️  @shell: 'hello'
    ✉️  @hello_bot: 'Hi!' {'text': 'Hi!'}
    ⚡ ︎ @shell: 'shell-ready'
    〉


Right after you hit ENTER, you will see ``✉️  @shell: 'hello'``, which is the shell broadcasting
your input as Message to 'test_space', which triggers the ``on_hello()`` method on ``hello_bot``
which we decorated with ``@on_message('hello')``.

The ``on_hello()`` "handler", as we call them in this codebase, simply returns a 'Hi!', which
is broadcast back to the space as a ``message`` with its ``reply_to`` set to the ``message.id``
of the message that triggered the handler.

This shows up in our shell as ``✉️  @hello_bot: 'Hi!' {'text': 'Hi!'}`` followed by the shell
emitting ``shell-ready`` event.

Seems like a lot for a hello world? Wait, let me show you this little trick... how much effort
do you think it would be, say, to create a slack bot that simply responds to "hello" with "hi"?

1. Add ``from zentropi.extra.agents import SlackAgent`` with rest of the imports
   at the top of ``hello.py``. This imports a helper agent that will relay messages between
   Slack and Zentropi.
2. Add ``slack_agent = SlackAgent('hello_slack')`` just before the last line.
3. Update the last line:

::

    run_agents(shell, hello_bot, join='test_space', endpoint='inmemory://test')

To look like this:

::

    run_agents(shell, hello_bot, slack_agent, join='test_space', endpoint='inmemory://test')

4. And finally, add ``export SLACK_BOT_API_KEY="[YOUR-API-KEY]"`` to your ``.bash_profile``
   or another preferred way to set environment variables, and run ``python hello.py`` again.

Yup, that's it :)

Would you think it cool if you could say, add an agent for Twitter in as many steps and
have a bot that works with Slack *and* Twitter, from the same Python process?

However, don't let this example make you think Zentropi is a tool to make chat-bots;
using this feature, we can build agents that can be accessed by humans with simple
text-commands as well as by software through states, events, requests and of course,
messages as well.

Zentropi is your medium and toolbox to make software that draws no unnecessary lines
between machines and people. We are all computing machines of varying capacities,
and an inclusive approach that enables each one of us to be better at what we want
to do is a honking good strategy!

It should not matter whether machines are big or small - as long as Python-3.5+
(and soon, Micropython) is available and minimum security expectations are met, we can
run Zentropian agents. It should not matter whether people access the agent from a mobile
phone app, a webapp, a command line interface or an accessibility device - a human mind
is as capable as another, irregardless of the body they occupy. We admit, that like
untrained neural networks and hardware that does not cooperate - human (and animal)
brains, the hardware our minds run on, can be less than perfect; the frustrations of
a conscious mind operating a faulty body, on a ill-cooperating hardware are many;
and it would be a shame if we left out machines or humans because we were too lazy
to consider them in our original plans.

There is more, much more on the way, watch this repo or better, fork this repo,
contribute and help us make it all real sooner!
