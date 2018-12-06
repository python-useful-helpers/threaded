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

"""Threaded implementation.

Asyncio is supported
"""

import functools
import threading
import typing

from . import class_decorator

__all__ = ("Threaded", "threaded")


class Threaded(class_decorator.BaseDecorator):
    """Run function in separate thread."""

    __slots__ = ("__name", "__daemon", "__started")

    def __init__(
        self,
        name: typing.Optional[
            typing.Union[str, typing.Callable[..., typing.Union["typing.Awaitable", typing.Any]]]
        ] = None,
        daemon: bool = False,
        started: bool = False,
    ) -> None:
        """Run function in separate thread.

        :param name: New thread name.
                     If callable: use as wrapped function.
                     If none: use wrapped function name.
        :type name: typing.Optional[typing.Union[str, typing.Callable[..., typing.Union[typing.Awaitable, typing.Any]]]]
        :param daemon: Daemonize thread.
        :type daemon: bool
        :param started: Return started thread
        :type started: bool
        """
        # pylint: disable=assigning-non-slot
        self.__daemon = daemon
        self.__started = started
        if callable(name):
            func = name  # type: typing.Callable
            self.__name = "Threaded: " + getattr(name, "__name__", str(hash(name)))  # type: str
        else:
            func, self.__name = None, name  # type: ignore
        super(Threaded, self).__init__(func=func)
        # pylint: enable=assigning-non-slot

    @property
    def name(self) -> typing.Optional[str]:
        """Thread name.

        :rtype: typing.Optional[str]
        """
        return self.__name

    @property
    def daemon(self) -> bool:
        """Start thread as daemon.

        :rtype: bool
        """
        return self.__daemon

    @property
    def started(self) -> bool:
        """Return started thread.

        :rtype: bool
        """
        return self.__started

    def __repr__(self) -> str:
        """For debug purposes."""
        return (
            "{cls}("
            "name={self.name!r}, "
            "daemon={self.daemon!r}, "
            "started={self.started!r}, "
            ")".format(cls=self.__class__.__name__, self=self)
        )  # pragma: no cover

    def _get_function_wrapper(
        self, func: typing.Callable[..., typing.Union["typing.Awaitable", typing.Any]]
    ) -> typing.Callable[..., threading.Thread]:
        """Here should be constructed and returned real decorator.

        :param func: Wrapped function
        :type func: typing.Callable[..., typing.Union[typing.Awaitable, typing.Any]]
        :return: wrapped function
        :rtype: typing.Callable[..., threading.Thread]
        """
        prepared = self._await_if_required(func)
        name = self.name
        if name is None:
            name = "Threaded: " + getattr(func, "__name__", str(hash(func)))

        # noinspection PyMissingOrEmptyDocstring
        @functools.wraps(prepared)  # pylint: disable=missing-docstring
        def wrapper(*args, **kwargs):  # type: (typing.Any, typing.Any) -> threading.Thread
            thread = threading.Thread(target=prepared, name=name, args=args, kwargs=kwargs, daemon=self.daemon)
            if self.started:
                thread.start()
            return thread

        return wrapper

    def __call__(  # pylint: disable=useless-super-delegation
        self,
        *args: typing.Union[typing.Callable[..., typing.Union["typing.Awaitable", typing.Any]], typing.Any],
        **kwargs: typing.Any
    ) -> typing.Union[threading.Thread, typing.Callable[..., threading.Thread]]:
        """Executable instance."""
        return super(Threaded, self).__call__(*args, **kwargs)  # type: ignore


# pylint: disable=function-redefined, unused-argument
@typing.overload
def threaded(
    name: typing.Callable, daemon: bool = False, started: bool = False
) -> typing.Callable[..., threading.Thread]:
    """Overload: Call decorator without arguments."""


@typing.overload  # noqa: F811
def threaded(name: typing.Optional[str] = None, daemon: bool = False, started: bool = False) -> Threaded:
    """Overload: Name is not callable."""


# pylint: enable=unused-argument
def threaded(  # noqa: F811
    name: typing.Optional[typing.Union[str, typing.Callable]] = None, daemon: bool = False, started: bool = False
) -> typing.Union[Threaded, typing.Callable[..., threading.Thread]]:
    """Run function in separate thread.

    :param name: New thread name.
                 If callable: use as wrapped function.
                 If none: use wrapped function name.
    :type name: typing.Union[None, str, typing.Callable]
    :param daemon: Daemonize thread.
    :type daemon: bool
    :param started: Return started thread
    :type started: bool
    :return: Threaded instance, if called as function or argumented decorator, else callable wraper
    :rtype: typing.Union[Threaded, typing.Callable[..., threading.Thread]]
    """
    if callable(name):
        func, name = (name, "Threaded: " + getattr(name, "__name__", str(hash(name))))
        return Threaded(name=name, daemon=daemon, started=started)(func)  # type: ignore
    return Threaded(name=name, daemon=daemon, started=started)


# pylint: enable=function-redefined
