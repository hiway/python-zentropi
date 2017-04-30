============
Installation
============

At the command line::

    pip install zentropi


Linux
=====

Tested on Ubuntu 16.04

We will need to set up Ubuntu for Python development before we can
install and use Zentropi, follow the steps below to update your
system with necessary packages:

1. Confirm that Python 3.5 is available
---------------------------------------

::
    $ sudo apt update
    $ sudo apt install python3
    $ python3 -V

Above command should output text similar to ``Python 3.5.X``;
at the time of writing, it was ``Python 3.5.2``.

If the command fails, run ``sudo apt install python3``.

2. Install external requirements
--------------------------------

We will first set up the tools to compile and install Python libraries
that are needed by Zentropi.

::

    $ sudo apt install gcc libssl-dev python3-dev python3-setuptools



3. Install and create a venv (python virtual-environment)

::

    $ sudo apt install python3-venv
    $ python3 -m venv zen

4. Activate the venv

::

    $ source zen/bin/activate

5. Install zentropi

::

    $ pip install zentropi

