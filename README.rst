========
Overview
========

.. start-badges

.. list-table::
    :stub-columns: 1

    * - docs
      - | |docs|
    * - tests
      - | |travis|
        | |requires|
    * - package
      - | |license| |version| |wheel|
        | |supported_versions| |supported_implementations|
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


Installation
============

::

    pip3 install zentropi

Documentation
=============

https://zentropi.readthedocs.io/


Example
=======

We will make a toy agent that responds to the message "hello" with a "hello, world".

.. image:: https://cloud.githubusercontent.com/assets/23116/25562708/1d83f7b4-2dab-11e7-988a-bccb2862b656.png

The above illustration shows how the concepts and objects are logically arranged and connected within Zentropi.
We will go deeper into these in the READMEs along with examples, for now let us jump straight to the code:

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

::

    $ python hello.py
    ⚡ ︎ @shell: '*** started'
    ⚡ ︎ @shell: 'shell-starting'
    ⚡ ︎ @shell: 'shell-ready'
    〉

We can type any message at the prompt ``〉`` and the shell agent will
broadcast it for us. Go ahead and type ``hello``, followed by ENTER.

::

    〉hello
    ✉  @shell: 'hello'
    ✉  @hello_bot: 'hello, world' {'text': 'hello, world'}
    ⚡ ︎ @shell: 'shell-ready'
    〉exit

Type ``exit`` or press Ctrl-D to leave the shell.

What next?

Zentropi is still being developed and is not production-ready, however
it is already useful to experiment and build toys.

Check out what is already possible in the examples directory:

https://github.com/zentropi/python-zentropi/tree/master/examples
