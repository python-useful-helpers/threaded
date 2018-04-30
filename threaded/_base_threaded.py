#    Copyright 2017-2018 Alexey Stepanov aka penguinolog
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
import typing  # noqa  # pylint: disable=unused-import

import six

from . import _class_decorator

if six.PY3:  # pragma: no cover
    from os import cpu_count
else:  # pragma: no cover
    try:
        from multiprocessing import cpu_count
    except ImportError:
        def cpu_count():  # type: () -> int
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

    __executor = None  # type: typing.Optional[typing.Any]

    @classmethod
    @abc.abstractmethod
    def configure(
        cls,
        max_workers=None,  # type: typing.Optional[int]
    ):  # type: (...) -> None
        """Pool executor create and configure.

        :param max_workers: Maximum workers
        :type max_workers: typing.Optional[int]
        """
        raise NotImplementedError()  # pragma: no cover

    @classmethod
    @abc.abstractmethod
    def shutdown(cls):  # type: () -> None
        """Shutdown executor."""
        raise NotImplementedError()  # pragma: no cover

    @property
    @abc.abstractmethod
    def executor(self):  # type: () -> typing.Any
        """Executor instance."""
        raise NotImplementedError()  # pragma: no cover


class BasePooled(APIPooled):
    """Base ThreadPooled class."""

    __slots__ = ()

    __executor = None  # type: typing.Optional[ThreadPoolExecutor]

    @classmethod
    def configure(
        cls,
        max_workers=None,  # type: int
    ):  # type: (...) -> None
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
    def shutdown(cls):  # type: () -> None
        """Shutdown executor."""
        if cls.__executor is not None:
            cls.__executor.shutdown()

    @property
    def executor(self):  # type: () -> ThreadPoolExecutor
        """Executor instance.

        :rtype: ThreadPoolExecutor
        """
        if (
            not isinstance(self.__executor, ThreadPoolExecutor) or
            self.__executor.is_shutdown
        ):
            self.configure()
        return self.__executor

    def _get_function_wrapper(
        self,
        func  # type: typing.Callable
    ):  # type: (...) -> typing.Callable[..., concurrent.futures.Future]
        """Here should be constructed and returned real decorator.

        :param func: Wrapped function
        :type func: typing.Callable
        :return: wrapped function
        :rtype: typing.Callable[..., concurrent.futures.Future]
        """
        # pylint: disable=missing-docstring
        # noinspection PyMissingOrEmptyDocstring
        @six.wraps(func)
        def wrapper(
            *args,
            **kwargs
        ):  # type: (...) -> concurrent.futures.Future
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
        name=None,  # type: typing.Optional[typing.Union[str, typing.Callable]]
        daemon=False,  # type: bool
        started=False,  # type: bool
    ):  # type: (...) -> None
        """Run function in separate thread.

        :param name: New thread name.
                     If callable: use as wrapped function.
                     If none: use wrapped function name.
        :type name: typing.Optional[typing.Union[str, typing.Callable]]
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
            )  # type: str
        else:
            func, self.__name = None, name  # type: None, typing.Optional[str]
        super(BaseThreaded, self).__init__(func=func)
        # pylint: enable=assigning-non-slot

    @property
    def name(self):  # type: () -> typing.Optional[str]
        """Thread name.

        :rtype: typing.Optional[str]
        """
        return self.__name

    @property
    def daemon(self):  # type: () -> bool
        """Start thread as daemon.

        :rtype: bool
        """
        return self.__daemon

    @property
    def started(self):  # type: () -> bool
        """Return started thread.

        :rtype: bool
        """
        return self.__started

    def _get_function_wrapper(
        self,
        func  # type: typing.Callable
    ):  # type: (...) -> typing.Callable[..., threading.Thread]
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
        def wrapper(
            *args,
            **kwargs
        ):  # type: (...) -> threading.Thread
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

    def __init__(
        self,
        max_workers=None  # type: typing.Optional[int]
    ):  # type: (...) -> None
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
    def max_workers(self):  # type: () -> int
        """MaxWorkers.

        :rtype: int
        """
        return self._max_workers

    @property
    def is_shutdown(self):  # type: () -> bool
        """Executor shutdown state.

        :rtype: bool
        """
        return self._shutdown
