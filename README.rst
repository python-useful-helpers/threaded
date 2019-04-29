threaded
========

.. image:: https://travis-ci.com/python-useful-helpers/threaded.svg?branch=master
    :target: https://travis-ci.com/python-useful-helpers/threaded
.. image:: https://coveralls.io/repos/github/python-useful-helpers/threaded/badge.svg?branch=master
    :target: https://coveralls.io/github/python-useful-helpers/threaded?branch=master
.. image:: https://readthedocs.org/projects/threaded/badge/?version=latest
    :target: https://threaded.readthedocs.io/
    :alt: Documentation Status
.. image:: https://img.shields.io/pypi/v/threaded.svg
    :target: https://pypi.python.org/pypi/threaded
.. image:: https://img.shields.io/pypi/pyversions/threaded.svg
    :target: https://pypi.python.org/pypi/threaded
.. image:: https://img.shields.io/pypi/status/threaded.svg
    :target: https://pypi.python.org/pypi/threaded
.. image:: https://img.shields.io/github/license/python-useful-helpers/threaded.svg
    :target: https://raw.githubusercontent.com/python-useful-helpers/threaded/master/LICENSE

threaded is a set of decorators, which wrap functions in:

  * `concurrent.futures.ThreadPool`
  * `threading.Thread`

Why? Because copy-paste of `loop.create_task`, `threading.Thread` and `thread_pool.submit` is boring,
especially if target functions is used by this way only.

Pros:

* Free software: Apache license
* Open Source: https://github.com/python-useful-helpers/threaded
* PyPI packaged: https://pypi.python.org/pypi/threaded
* Tested: see bages on top
* Support multiple Python versions:

::

    Python 2.7
    PyPy

.. note:: Update to version 2.0+ for usage with python 3.4+. This version is for legacy python and no new features are planned.

Decorators:

* `ThreadPooled` - native ``concurrent.futures.ThreadPool`` usage on Python 3 and it's backport on Python 2.7.
* `threadpooled` is alias for `ThreadPooled`.

* `Threaded` - wrap in ``threading.Thread``.
* `threaded` is alias for `Threaded`.

Usage
=====

ThreadPooled
------------
Mostly it is required decorator: submit function to ThreadPoolExecutor on call.

.. note::

    API quite differs between Python 3 and Python 2.7. See API section below.

.. code-block:: python

    threaded.ThreadPooled.configure(max_workers=3)

.. note::

    By default, if executor is not configured - it configures with default parameters: ``max_workers=(CPU_COUNT or 1) * 5``

Python 2.7 usage:

.. code-block:: python

    @threaded.ThreadPooled
    def func():
        pass

    concurrent.futures.wait([func()])

During application shutdown, pool can be stopped (while it will be recreated automatically, if some component will request).

.. code-block:: python

    threaded.ThreadPooled.shutdown()

Threaded
--------
Classic ``threading.Thread``. Useful for running until close and self-closing threads without return.

Usage example:

.. code-block:: python

    @threaded.Threaded
    def func(*args, **kwargs):
        pass

    thread = func()
    thread.start()
    thread.join()

Without arguments, thread name will use pattern: ``'Threaded: ' + func.__name__``

.. note::

    If func.__name__ is not accessible, str(hash(func)) will be used instead.

Override name can be don via corresponding argument:

.. code-block:: python

    @threaded.Threaded(name='Function in thread')
    def func(*args, **kwargs):
        pass

Thread can be daemonized automatically:

.. code-block:: python

    @threaded.Threaded(daemon=True)
    def func(*args, **kwargs):
        pass

Also, if no any addition manipulations expected before thread start,
it can be started automatically before return:

.. code-block:: python

    @threaded.Threaded(started=True)
    def func(*args, **kwargs):
        pass

Testing
=======
The main test mechanism for the package `threaded` is using `tox`.
Available environments can be collected via `tox -l`

CI systems
==========
For code checking several CI systems is used in parallel:

1. `Travis CI: <https://travis-ci.com/python-useful-helpers/threaded>`_ is used for checking: PEP8, pylint, bandit, installation possibility and unit tests. Also it's publishes coverage on coveralls.

2. `coveralls: <https://coveralls.io/github/python-useful-helpers/threaded>`_ is used for coverage display.

CD system
=========
`Travis CI: <https://travis-ci.com/python-useful-helpers/threaded>`_ is used for package delivery on PyPI.
