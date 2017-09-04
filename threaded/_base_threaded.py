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

import abc
# noinspection PyCompatibility
import concurrent.futures
import threading

import six

from . import _class_decorator

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
    'APIPooled',
    'BasePooled',
    'ThreadPoolExecutor',
    'cpu_count'
)


class APIPooled(_class_decorator.BaseDecorator):
    """API description for pooled."""

    __slots__ = ()

    __executor = None

    @classmethod
    @abc.abstractmethod
    def configure(
        cls,
        max_workers=None,
    ):
        """Pool executor create and configure.

        :param max_workers: Maximum workers
        :type max_workers: typing.Optional[int]
        """
        raise NotImplementedError()  # pragma: no cover

    @classmethod
    @abc.abstractmethod
    def shutdown(cls):
        """Shutdown executor."""
        raise NotImplementedError()  # pragma: no cover

    @property
    @abc.abstractmethod
    def executor(self):
        """Executor instance."""
        raise NotImplementedError()  # pragma: no cover


class BasePooled(APIPooled):
    """Base ThreadPooled class."""

    __slots__ = ()

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

    def _get_function_wrapper(self, func):
        """Here should be constructed and returned real decorator.

        :param func: Wrapped function
        :type func: typing.Callable
        :return: wrapped function
        :rtype: typing.Callable[..., concurrent.futures.Future]
        """
        # pylint: disable=missing-docstring
        # noinspection PyMissingOrEmptyDocstring
        @six.wraps(func)
        def wrapper(*args, **kwargs):
            return self.executor.submit(func, *args, **kwargs)
        # pylint: enable=missing-docstring
        return wrapper


class BaseThreaded(_class_decorator.BaseDecorator):
    """Base Threaded class."""

    __slots__ = (
        '__name',
        '__daemon',
        '__started',
    )

    def __init__(
        self,
        name=None,
        daemon=False,
        started=False,
    ):
        """Run function in separate thread.

        :param name: New thread name.
                     If callable: use as wrapped function.
                     If none: use wrapped function name.
        :type name: typing.Union[None, str, typing.Callable]
        :param daemon: Daemonize thread.
        :type daemon: bool
        :param started: Return started thread
        :type started: bool
        """
        # pylint: disable=assigning-non-slot
        self.__daemon = daemon
        self.__started = started
        if callable(name):
            func = name
            self.__name = 'Threaded: ' + getattr(
                name,
                '__name__',
                str(hash(name))
            )
        else:
            func, self.__name = None, name
        super(BaseThreaded, self).__init__(func=func)
        # pylint: enable=assigning-non-slot

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

    def _get_function_wrapper(self, func):
        """Here should be constructed and returned real decorator.

        :param func: Wrapped function
        :type func: typing.Callable
        :return: wrapped function
        :rtype: typing.Callable[..., threading.Thread]
        """
        name = self.name
        if name is None:
            name = 'Threaded: ' + getattr(
                func,
                '__name__',
                str(hash(func))
            )

        # pylint: disable=missing-docstring
        # noinspection PyMissingOrEmptyDocstring
        @six.wraps(func)
        def wrapper(*args, **kwargs):
            thread = threading.Thread(
                target=func,
                name=name,
                args=args,
                kwargs=kwargs,
            )
            thread.daemon = self.daemon
            if self.started:
                thread.start()
            return thread

        # pylint: enable=missing-docstring
        return wrapper

    def __repr__(self):
        """For debug purposes."""
        return (
            "{cls}("
            "name={self.name!r}, "
            "daemon={self.daemon!r}, "
            "started={self.started!r}, "
            ")".format(
                cls=self.__class__.__name__,
                self=self,
            )
        )  # pragma: no cover


class ThreadPoolExecutor(concurrent.futures.ThreadPoolExecutor):
    """Provide readers for protected attributes.

    Simply extend concurrent.futures.ThreadPoolExecutor.
    """

    __slots__ = ()

    def __init__(self, max_workers=None):
        """Override init due to difference between Python <3.5 and 3.5+.

        :param max_workers: Maximum workers allowed.
                            If none: cpu_count() or 1) * 5
        :type max_workers: typing.Optional[int]
        """
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
