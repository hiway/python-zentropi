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

.. |commits_since| image:: https://img.shields.io/github/commits-since/zentropi/python-zentropi/v0.1.0.svg
    :alt: Commits since latest release
    :target: https://github.com/zentropi/python-zentropi/compare/v0.1.0...master

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
concepts such as State, Event, Message and Request-Response*, each is implemented as
a simple to learn and easy to use API.

*Request-Response will be available soon.

Example:
--------

::

    # coding=utf-8
    from zentropi import Agent
    from zentropi import on_timer


    class Hello(Agent):
        @on_timer(1)
        def every_second(self):
            print('Hello, world!')

        @on_timer(3)
        def on_three_seconds(self):
            self.stop()


    agent = Hello()
    agent.run()


The above code can be saved as "hello.py" and run with "python hello.py"

It will print out "Hello, world!" a few times and stop.


Example: Telegram Bot + Relay Agent:
------------------------------------

Have a look at the examples folder, after you have installed zentropi,
you can try the examples with ::

    python {example_name.py}

Run these commands in examples folder in a separate terminal window/tab ::

    export TELEGRAM_BOT_API_TOKEN="{get your telegram api token from @botfather}"
    export TELEGRAM_BOT_NAME="ExampleBot"

    python 10_telegram_bot/telegram_bot.py

    python 11_relay/relay_agent.py

Now send "switch on" or "switch off" from your telegram account to your bot.

It should respond with "Switching power [on|off]" depending on your command,
as well as print out GPIO state in terminal.


Installation
============

::

    pip install zentropi

Documentation
=============

https://zentropi.readthedocs.io/
