============
Installation
============

If you already have virtual-environment and python-dev set up::

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

    $ sudo apt install gcc libssl-dev python3-dev python3-setuptools python3-venv


3. Install and create venv
--------------------------
::

    $ python3 -m venv zen


This creates a python virtual-environment, which keeps your installed
libraries separate from rest of the system.

4. Activate the venv
--------------------

::

    $ source zen/bin/activate


You will need to `activate` the zen virtual-environment before working
with zentropi. A shortcut would be to add an alias to your ``~/.profile``
or ``~/.bash_profile``:

::

    alias zen="source /path/to/zen/bin/activate"


You can run ``source ~/.profile`` or open a new terminal window
and type ``zen`` to activate the virtual-environment.

5. Install zentropi
-------------------

::

    $ pip install zentropi

