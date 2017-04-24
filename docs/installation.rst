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

    $ python3.5 -V

Above command should output text similar to ``Python 3.5.X``;
at the time of writing, it was ``Python 3.5.2``.

If the command fails, run ``sudo apt install python3.5``.


2. Install external requirements
--------------------------------

We will first set up the tools to compile and install Python libraries
that are needed by Zentropi.

::

    $ sudo apt install gcc libssl-dev python3-dev python3-setuptools


3. Install pip
--------------

Although Ubuntu 16.04 comes with python3.5 installed, it does not have
a necessary tool (pip) needed to install additional libraries in system python.
We can fix that with:

::

    $ wget https://bootstrap.pypa.io/get-pip.py
    $ sudo python3.5 get-pip.py

You may want to read more on the topic here: http://pip.readthedocs.io/en/latest/installing/#install-pip


4. Install and set up virtualenv
--------------------------------

Not strictly needed, however it is highly recommended to use ``virtualenv``
to isolate Python environments. Let us set it up because we care about our future self :)

::

    $ sudo pip3 install virtualenv
    $ virtualenv --python=`which python3.5` zen
    $ source zen/bin/activate
    (zen) $

You can run ``deactivate`` to disable the virtualenv in current session.

::

    (zen) $ deactivate
    $

Remember to run ``source zen/bin/activate`` in a new terminal session to activate the virtualenv.


6. Install zentropi inside virtualenv

::

    (zen) $ pip install zentropi

