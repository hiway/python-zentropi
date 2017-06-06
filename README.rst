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

.. |commits_since| image:: https://img.shields.io/github/commits-since/zentropi/python-zentropi/v0.1.3.svg
    :alt: Commits since latest release
    :target: https://github.com/zentropi/python-zentropi/compare/v0.1.3...master

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

Zentropi is a system that helps you create and mix-and-match agents as building blocks
to make your own automation.

Installation
============

Note: Requires Python 3.5+ and compiler toolchain to build c-extensions.

Stable:
-------

::

    $ python3 -m venv zen
    $ source zen/bin/activate
    $ pip install zentropi


Current:
--------

::

    $ python3 -m venv zen
    $ source zen/bin/activate
    $ git clone https://github.com/zentropi/python-zentropi.git
    $ cd python-zentropi
    $ pip install -e .


Install steps for Ubuntu and MacOS:
https://zentropi.readthedocs.io/en/latest/installation.html


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
        run_agents(hello_bot, shell=True)


Save this as ``hello.py`` and run with ``$ python hello.py``

You should see this on your screen:

::

    $ python hello.py
    ⚡ ︎ @shell: '*** started'
    〉

We can type any message at the prompt ``〉`` and the shell agent will
broadcast it for us. Go ahead and type ``hello``, followed by ENTER.

::

    〉hello
    ✉  @shell: 'hello'
    ✉  @hello_bot: 'hello, world'
    〉exit

Type ``exit`` or press Ctrl-D to leave the shell.

What next?

Zentropi is still being developed and is not production-ready, however
it is already useful to experiment and build toys.

Check out what is already possible in the examples directory:

https://github.com/zentropi/python-zentropi/tree/master/examples

Philosophy:
-----------

TL;DR: Zentropi is more than one thing, but they're all related.

    - It is the hypothesis/phenomenon that given enough energy
        and components capable of computing (that is, they can hold,
        replicate, transmit or transform information),
        any system - whether natural or artificial, can evolve
        into a system that requires and supports a mind.
    - It is a manifesto based on the implications of the
        hypothesis above, and guidelines that are used to build
        Zentropian Agents: software that is secure, resilient,
        fair and pragmatic about solving real problems.
    - It is a framework to write autonomous Agents, with the mental
        models and guidelines discussed in the manifesto
        implemented in Python; Open Source because good ideas
        whose time has come can not be shackled.
    - It is the company that provides subscription based
        services for customers who use the zentropi framework
        and would like to support its development, use agents
        hosted by zentropi or as a global network through
        shared and public spaces. (coming soon :)

