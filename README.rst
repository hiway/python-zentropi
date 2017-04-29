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

Why Zentropi?

- Comes with a simple mental model to write, deploy, share and maintain distributed autonomous agents.
- Built from ground up to be approachable and hackable, build systems you can take apart and change with confidence.
- Friendly: uses simple and distinct names to reduce cognitive load, does not expect English to be your native language.
- Flexible: experiment with multiple agents running in a single python process before you split each agent
  into a separate process on the same machine or across the planet. Or perhaps, run a whole bunch of agents
  as one process to keep their internal communication off of networks.
- Security and privacy are built-in and expected.


---

Zentropi is built around the concepts of `Agent`s, `Space`s and
`Frame`s. Using these concepts, we can imagine, design and create
agents of varying capabilities.

`python-zentropi` is the work-in-progress implementation of these
concepts using Python 3.5.

Installation
============

::

    pip install zentropi

Documentation
=============

https://zentropi.readthedocs.io/


Example
=======

Let us pretend we are leading a group

::

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
        run_agents(shell, warrior, join='Thermopylae', endpoint='inmemory://')




Save this as "one_spartan.py"

Let us run it using the command:
::

    $ python one_spartan.py


We can now interact with our newly created agent using our built-in shell prompt.
While starting up, the shell itself emits events, which you can see displayed
on the screen as ``⚡ ︎ @shell: 'shell-starting'`` followed by ``⚡ ︎ @shell: 'shell-ready'``.

You will be presented with a prompt ``〉``, where you can type in messages to be broadcast
to all the spaces that the shell has joined. Go ahead and call your warrior with "Spartans?",
followed by ENTER key.

::

    $ python one_spartan.py
    ⚡ ︎ @shell: 'shell-starting'
    ⚡ ︎ @shell: 'shell-ready'
    〉Spartans?
    ✉️  @shell: 'Spartans?'
    ✉️  @Spartan: 'Ahoo!' {'text': 'Ahoo!'}
    ⚡ ︎ @shell: 'shell-ready'
    〉


Right after you hit ENTER, you will see ``✉️  @shell: 'Spartans?'``, which is the shell broadcasting
your input as Message, which triggers the ``on_hello()`` method on ``hello_bot``
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

What next?

Play with [the examples](https://github.com/zentropi/python-zentropi/tree/master/examples)
and put together something fun over a weekend?

