#    Copyright 2017 Alexey Stepanov aka penguinolog
##
#    Licensed under the Apache License, Version 2.0 (the "License"); you may
#    not use this file except in compliance with the License. You may obtain
#    a copy of the License at
#
#         http://www.apache.org/licenses/LICENSE-2.0
#
#    Unless required by applicable law or agreed to in writing, software
#    distributed under the License is distributed on an "AS IS" BASIS, WITHOUT
#    WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the
#    License for the specific language governing permissions and limitations
#    under the License.

"""Base classes for ThreadPooled and Threaded."""

from __future__ import absolute_import
from __future__ import unicode_literals

import abc
# noinspection PyCompatibility
import concurrent.futures
import functools
import typing

import six

if six.PY3:  # pragma: no cover
    from os import cpu_count
else:  # pragma: no cover
    try:
        from multiprocessing import cpu_count
    except ImportError:
        def cpu_count():
            """Fake CPU count."""
            return 1

__all__ = (
    'BasePooled',
    'ThreadPoolExecutor',
)


class BasePooled(
    type.__new__(
        abc.ABCMeta,
        'BasePooled' if six.PY3 else b'BasePooled',
        (typing.Callable, ),
        {}
    )
):
    """Base ThreadPooled class."""

    __slots__ = (
        '__func',
        '__wrapped__',
    )

    __executor = None

    @classmethod
    def configure(
        cls,
        max_workers=None,
    ):
        """Pool executor create and configure.

        :param max_workers: Maximum workers
        :type max_workers: typing.Optional[int]
        """
        if isinstance(cls.__executor, ThreadPoolExecutor):
            if cls.__executor.max_workers == max_workers:
                return
            cls.__executor.shutdown()

        cls.__executor = ThreadPoolExecutor(
            max_workers=max_workers,
        )

    @classmethod
    def shutdown(cls):
        """Shutdown executor."""
        if cls.__executor is not None:
            cls.__executor.shutdown()

    @property
    def executor(self):
        """Executor instance.

        :rtype: ThreadPoolExecutor
        """
        if (
            not isinstance(self.__executor, ThreadPoolExecutor) or
            self.__executor.is_shutdown
        ):
            self.configure()
        return self.__executor

    def __init__(self, func=None):
        """Pooled decorator.

        :param func: function to wrap
        :type func: typing.Callable[]
        """
        # pylint: disable=assigning-non-slot
        self.__func = func
        if self.__func is not None:
            functools.update_wrapper(self, self.__func)
            if not six.PY34:  # pragma: no cover
                self.__wrapped__ = self.__func
        # pylint: enable=assigning-non-slot
        # noinspection PyArgumentList
        super(BasePooled, self).__init__()

    @abc.abstractmethod
    def _get_function_wrapper(self, func):
        """Here should be constructed and returned real decorator.

        :param func: Wrapped function
        :type func: typing.Callable
        :rtype: typing.Callable
        """
        raise NotImplementedError()  # pragma: no cover

    def __call__(self, *args, **kwargs):
        """Main decorator getter.

        :returns: Decorated function. On python 3.3+ asyncio.Task is supported.
        :rtype: typing.Union[typing.Callable, concurrent.futures.Future]
        """
        args = list(args)
        wrapped = self.__func or args.pop(0)
        wrapper = self._get_function_wrapper(wrapped)
        if self.__func:
            return wrapper(*args, **kwargs)
        return wrapper

    def __repr__(self):
        """For debug purposes."""
        return "<{cls}({func!r}) at 0x{id:X}>".format(
            cls=self.__class__.__name__,
            func=self.__func,
            id=id(self)
        )  # pragma: no cover


class BaseThreaded(
    type.__new__(
        abc.ABCMeta,
        'BaseThreaded' if six.PY3 else b'BaseThreaded',
        (typing.Callable, ),
        {}
    )
):
    """Base Threaded class."""

    __slots__ = (
        '__func',
        '__name',
        '__daemon',
        '__started',
        '__wrapped__',
    )

    def __init__(
        self,
        name=None,
        daemon=False,
        started=False,
    ):
        """Threaded decorator.

        :param name: New thread name.
        :type name: typing.Callable
        :param daemon: Daemonize thread.
        :type daemon: bool
        :param started: Return started thread
        :type started: bool
        """
        # pylint: disable=assigning-non-slot
        self.__daemon = daemon
        self.__started = started
        if callable(name):
            self.__func = name
            self.__name = 'Threaded: ' + getattr(
                name,
                '__name__',
                str(hash(name))
            )
        else:
            self.__func, self.__name = None, name

        if self.__func is not None:
            functools.update_wrapper(self, self.__func)
            if not six.PY34:  # pragma: no cover
                self.__wrapped__ = self.__func
        # pylint: enable=assigning-non-slot
        # noinspection PyArgumentList
        super(BaseThreaded, self).__init__()

    @property
    def name(self):
        """Thread name.

        :rtype: typing.Optional[str]
        """
        return self.__name

    @property
    def daemon(self):
        """Start thread as daemon.

        :rtype: bool
        """
        return self.__daemon

    @property
    def started(self):
        """Return started thread.

        :rtype: bool
        """
        return self.__started

    @abc.abstractmethod
    def _get_function_wrapper(self, func):
        """Here should be constructed and returned real decorator.

        :param func: Wrapped function
        :type func: typing.Callable
        :rtype: typing.Callable
        """
        raise NotImplementedError()  # pragma: no cover

    def __call__(self, *args, **kwargs):
        """Main decorator getter.

        :returns: Decorated function. On python 3.3+ asyncio.Task is supported.
        :rtype: typing.Union[typing.Callable, concurrent.futures.Future]
        """
        args = list(args)
        wrapped = self.__func or args.pop(0)
        wrapper = self._get_function_wrapper(wrapped)
        if self.__func:
            return wrapper(*args, **kwargs)
        return wrapper

    def __repr__(self):
        """For debug purposes."""
        return (
            "{cls}("
            "{func!r}, "
            "name={self.name!r}, "
            "daemon={self.daemon!r}, "
            "started={self.started!r}, "
            ")".format(
                cls=self.__class__.__name__,
                func=self.__func,
                self=self,
            )
        )  # pragma: no cover


class ThreadPoolExecutor(concurrent.futures.ThreadPoolExecutor):
    """Readers for protected attributes."""

    __slots__ = ()

    def __init__(self, max_workers=None):
        """Override init due to difference between Python <3.5 and 3.5+."""
        if max_workers is None:  # Use 3.5+ behavior
            max_workers = (cpu_count() or 1) * 5
        super(
            ThreadPoolExecutor,
            self
        ).__init__(
            max_workers=max_workers,
        )

    @property
    def max_workers(self):
        """MaxWorkers.

        :rtype: int
        """
        return self._max_workers

    @property
    def is_shutdown(self):
        """Executor shutdown state.

        :rtype: bool
        """
        return self._shutdown
