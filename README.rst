threaded
========

.. image:: https://travis-ci.org/penguinolog/threaded.svg?branch=master
    :target: https://travis-ci.org/penguinolog/threaded
.. image:: https://img.shields.io/pypi/v/threaded.svg
    :target: https://pypi.python.org/pypi/threaded
.. image:: https://img.shields.io/pypi/pyversions/threaded.svg
    :target: https://pypi.python.org/pypi/threaded
.. image:: https://img.shields.io/pypi/status/threaded.svg
    :target: https://pypi.python.org/pypi/threaded
.. image:: https://img.shields.io/github/license/penguinolog/threaded.svg
    :target: https://raw.githubusercontent.com/penguinolog/threaded/master/LICENSE

threaded is a set of decorators, which wrap functions in concurrent.futures.ThreadPool and asyncio.Task in Python 3.
Why? Because copy-paste of `loop.create_task` and `thread_pool.submit()` is boring,
especially if target functions is used by this way only.

Pros:

* Free software: Apache license
* Open Source: https://github.com/penguinolog/threaded
* PyPI packaged: https://pypi.python.org/pypi/threaded
* Tested: see bages on top
* Support multiple Python versions:

::

    Python 2.7
    Python 3.4
    Python 3.5
    Python 3.6
    PyPy
    PyPy3 3.5+
    Jyton 2.7

Decorators:

* `ThreadPooled` - native concurrent.futures.ThreadPool usage on Python 3 and backport on Python 2.7.
* `threadpooled` is alias for `ThreadPooled`.

* `Threaded` - wrap in threading.Thread.
* `threaded` is alias for `Threaded`.

* `AsyncIOTask` - wrap in asyncio.Task. Uses the same API, as Python 3 `ThreadPooled`.
* `asynciotask` is alias for `AsyncIOTask`.

Usage
=====

ThreadPooled
------------
Mostly it is required decorator: submit function to ThreadPoolExecutor on call.

.. note:: API quite differs between Python 3 and Python 2.7.

Python 2.7 usage from signature:

.. code-block:: python

    threaded.ThreadPooled.configure(max_workers=None)  # Not mandatory.
    # max_workers=None means (CPU_COUNT or 1) * 5, it's default value.
    @threaded.ThreadPooled  # Arguments not accepted, so `()` is useless
    def func():
        pass

    concurrent.futures.wait([func()])

Python 3.3+ usage from signature:

.. code-block:: python

    threaded.ThreadPooled.configure(max_workers=None)
    @threaded.ThreadPooled(loop_getter=None, loop_getter_need_context=False)  # strictly keyword arguments. See details below.
    # For standard concurrent.futures, arguments is useless and should be omitted (use like Python 2 version)
    def func():
        pass

    concurrent.futures.wait([func()])

Python 3.3+ usage with asyncio:

.. code-block:: python3

    loop = asyncio.get_event_loop()
    threaded.ThreadPooled.configure(max_workers=None)
    @threaded.ThreadPooled(loop_getter=loop, loop_getter_need_context=False)  # provide loop directly -> loop_getter_need_context will be ignored
    def func():
        pass

    loop.run_until_complete(asyncio.wait_for(func(), timeout))  # func() will return asyncio.Task bound with decorator argument.

Python 3.3+ usage with asyncio and loop extraction from call arguments:

.. code-block:: python3

    loop_getter = lambda tgt_loop: tgt_loop
    threaded.ThreadPooled.configure(max_workers=None)
    @threaded.ThreadPooled(loop_getter=loop_getter, loop_getter_need_context=True)  # loop_getter_need_context is required
    def func(*args, **kwargs):
        pass

    loop = asyncio.get_event_loop()
    loop.run_until_complete(asyncio.wait_for(func(loop), timeout))  # func() will return asyncio.Task bound with loop from argument.

Threaded
--------
Classic threading.Thread. Useful for running until close and self-closing threads without return.

Usage example with all arguments:

.. code-block:: python

    @threaded.Threaded(name=None, daemon=False, started=False)  # All defaults. Name will be used from wrapped function.
    def func(*args, **kwargs):
        pass

    thread = func()
    thread.start()
    thread.join()

If need to use wit all defaults, arguments may be completely omitted:

.. code-block:: python

    @threaded.Threaded
    def func(*args, **kwargs):
        pass

AsyncIOTask
-----------
Wrap in asyncio.Task.

usage with asyncio:

.. code-block:: python3

    loop = asyncio.get_event_loop()
    threaded.ThreadPooled.configure(max_workers=None)
    @threaded.ThreadPooled(loop_getter=loop, loop_getter_need_context=False)  # provide loop directly -> loop_getter_need_context will be ignored
    # By default asyncio.get_event_loop is used, so technically, with single asyncio loop, we can use without arguments.
    def func():
        pass

    loop.run_until_complete(asyncio.wait_for(func(), timeout))  # func() will return asyncio.Task bound with decorator argument.

Usage with asyncio and loop extraction from call arguments:

.. code-block:: python3

    loop_getter = lambda tgt_loop: tgt_loop
    threaded.ThreadPooled.configure(max_workers=None)
    @threaded.ThreadPooled(loop_getter=loop_getter, loop_getter_need_context=True)  # loop_getter_need_context is required
    def func(*args, **kwargs):
        pass

    loop = asyncio.get_event_loop()
    loop.run_until_complete(asyncio.wait_for(func(loop), timeout))  # func() will return asyncio.Task bound with loop from argument.

Testing
=======
The main test mechanism for the package `threaded` is using `tox`.
Test environments available:

::

    pep8
    py27
    py34
    py35
    py36
    pypy
    pypy3
    pylint
