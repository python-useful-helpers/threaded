threaded
========

.. image:: https://travis-ci.com/python-useful-helpers/threaded.svg?branch=master
    :target: https://travis-ci.com/python-useful-helpers/threaded
.. image:: https://dev.azure.com/python-useful-helpers/threaded/_apis/build/status/python-useful-helpers.threaded?branchName=master
    :alt: Azure DevOps builds
    :target: https://dev.azure.com/python-useful-helpers/threaded/_build?definitionId=3
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
.. image:: https://img.shields.io/badge/code%20style-black-000000.svg
    :target: https://github.com/ambv/black

threaded is a set of decorators, which wrap functions in:

  * `concurrent.futures.ThreadPool`
  * `threading.Thread`
  * `asyncio.Task` in Python 3.

Why? Because copy-paste of `loop.create_task`, `threading.Thread` and `thread_pool.submit` is boring,
especially if target functions is used by this way only.

Pros:

* Free software: Apache license
* Open Source: https://github.com/python-useful-helpers/threaded
* PyPI packaged: https://pypi.python.org/pypi/threaded
* Tested: see bages on top
* Support multiple Python versions:

::

    Python 3.4
    Python 3.5
    Python 3.6
    Python 3.7
    PyPy3 3.5+

.. note:: For python 2.7/PyPy you can use versions 1.x.x

Decorators:

* `ThreadPooled` - native ``concurrent.futures.ThreadPool``.
* `threadpooled` is alias for `ThreadPooled`.

* `Threaded` - wrap in ``threading.Thread``.
* `threaded` is alias for `Threaded`.

* `AsyncIOTask` - wrap in ``asyncio.Task``. Uses the same API, as `ThreadPooled`.
* `asynciotask` is alias for `AsyncIOTask`.

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

    By default, if executor is not configured - it configures with default parameters: ``max_workers=CPU_COUNT * 5``

.. code-block:: python

    @threaded.ThreadPooled
    def func():
        pass

    concurrent.futures.wait([func()])

Python 3.5+ usage with asyncio:

.. note::

    if `loop_getter` is not callable, `loop_getter_need_context` is ignored.

.. code-block:: python

    loop = asyncio.get_event_loop()
    @threaded.ThreadPooled(loop_getter=loop, loop_getter_need_context=False)
    def func():
        pass

    loop.run_until_complete(asyncio.wait_for(func(), timeout))

Python 3.5+ usage with asyncio and loop extraction from call arguments:

.. code-block:: python

    loop_getter = lambda tgt_loop: tgt_loop
    @threaded.ThreadPooled(loop_getter=loop_getter, loop_getter_need_context=True)  # loop_getter_need_context is required
    def func(*args, **kwargs):
        pass

    loop = asyncio.get_event_loop()
    loop.run_until_complete(asyncio.wait_for(func(loop), timeout))

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

AsyncIOTask
-----------
Wrap in ``asyncio.Task``.

usage with asyncio:

.. code-block:: python

    @threaded.AsyncIOTask
    def func():
        pass

    loop = asyncio.get_event_loop()
    loop.run_until_complete(asyncio.wait_for(func(), timeout))

Provide event loop directly:

.. note::

    if `loop_getter` is not callable, `loop_getter_need_context` is ignored.

.. code-block:: python

    loop = asyncio.get_event_loop()
    @threaded.AsyncIOTask(loop_getter=loop)
    def func():
        pass

    loop.run_until_complete(asyncio.wait_for(func(), timeout))

Usage with loop extraction from call arguments:

.. code-block:: python

    loop_getter = lambda tgt_loop: tgt_loop
    @threaded.AsyncIOTask(loop_getter=loop_getter, loop_getter_need_context=True)
    def func(*args, **kwargs):
        pass

    loop = asyncio.get_event_loop()
    loop.run_until_complete(asyncio.wait_for(func(loop), timeout))

Testing
=======
The main test mechanism for the package `threaded` is using `tox`.
Available environments can be collected via `tox -l`

CI systems
==========
For code checking several CI systems is used in parallel:

1. `Travis CI: <https://travis-ci.com/python-useful-helpers/threaded>`_ is used for checking: PEP8, pylint, bandit, installation possibility and unit tests. Also it's publishes coverage on coveralls.

2. `coveralls: <https://coveralls.io/github/python-useful-helpers/threaded>`_ is used for coverage display.

3. `Azure CI: <https://dev.azure.com/python-useful-helpers/threaded/_build?definitionId=3>`_ is used for functional tests on Windows.

CD system
=========
`Travis CI: <https://travis-ci.com/python-useful-helpers/threaded>`_ is used for package delivery on PyPI.
