==========
 pygetent
==========

Python interface to the POSIX getent family of commands (getpwent, getgrent, getnetent, etc.)


Usage
=====

Here a few examples.

Load the interface::

    >>> import pygetent as getent

Doing a passwd lookup::

    >>> print dict(getent.passwd('root'))
    {'dir': '/root',
     'gecos': 'root',
     'gid': 0,
     'name': 'root',
     'password': 'x',
     'shell': '/bin/bash',
     'uid': 0}

Doing a group lookup::

    >>> print dict(getent.group('root'))
    {'gid': 0, 'members': [], 'name': 'root', 'password': 'x'}


Bugs
====

Please use the `bug tracker at GitHub`_ for bugs or feature requests.

.. _bug tracker at GitHub: https://github.com/screamingpigeon/getent/issues


Authors
=======

* `Wijnand Modderman-Lenstra <https://maze.io/>`_
* Thomas Kula
* `Olivier Cortès <http://oliviercortes.com/>`_
* Forked by Prakhar Gupta

Build status
============

.. image:: https://landscape.io/github/tehmaze/getent/master/landscape.svg
   :target: https://landscape.io/github/tehmaze/getent/master

.. image:: https://travis-ci.org/tehmaze/getent.svg
   :target: https://travis-ci.org/tehmaze/getent

.. image:: https://coveralls.io/repos/tehmaze/getent/badge.svg
   :target: https://coveralls.io/r/tehmaze/getent

Why was this forked?
====================
Originally forked from https://github.com/tehmaze/getent. This fork was created since 
 A) the original repository is now archived
 B) The package published to pypi has a broken setup.py, which leads to installation failure. This was due to the `file()` function being called on this very Readme. While the original repository reflects an update that uses 'read()`, the PyPi source has not been updated. This repository exists to republish to PyPI
