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

::

    from zentropi import Agent, on_message, run_agents, ZentropiShell


    class HelloBot(Agent):
        @on_message('hello')
        def say_hello(self, message):
            return 'hello, world'


    if __name__ == '__main__':
        hello_bot = HelloBot(name='hello_bot')
        shell = ZentropiShell(name='shell')
        run_agents(hello_bot, shell)


Save this as ``hello.py`` and run with ``$ python hello.py``

You should see this on your screen:

```
$ python hello.py
⚡ ︎ @shell: '*** started'
⚡ ︎ @shell: 'shell-starting'
⚡ ︎ @shell: 'shell-ready'
〉
```

We can type any message at the prompt `〉` and the shell agent will
broadcast it for us. Go ahead and type "hello", followed by ENTER.

```
〉hello
✉  @shell: 'hello'
✉  @hello_bot: 'hello, world' {'text': 'hello, world'}
⚡ ︎ @shell: 'shell-ready'
〉
```

If you see this, hooray! You've created your first Zentropian Agent!

Don't let this single example give you the impression that Zentropi is about chat-bots,
it is a generic communication system that works for machines as well as humans, hence
text messages are a first-class member in Zentropi, along with events that are generally
used for asynchronous machine-to-machine communication.

What next? See [examples](https://github.com/zentropi/python-zentropi/tree/master/examples)
for detailed instructions along with each example agent and dig up your ideas that have
been waiting too long to be made real!
