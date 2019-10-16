#    Copyright 2017 - 2019 Alexey Stepanov aka penguinolog
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

from threaded cimport class_decorator

cpdef tuple __all__ = ("Threaded", "threaded")


cdef class Threaded(class_decorator.BaseDecorator):
    """Run function in separate thread."""


    def __init__(
        self,
        name: typing.Optional[
            typing.Union[str, typing.Callable[..., typing.Union["typing.Awaitable", typing.Any]]]
        ] = None,
        bint daemon = False,
        bint started = False,
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
        self.daemon = daemon
        self.started = started
        if callable(name):
            func = name  # type: typing.Callable
            self.name = "Threaded: " + getattr(name, "__name__", str(hash(name)))  # type: str
        else:
            func, self.name = None, name  # type: ignore
        super(Threaded, self).__init__(func=func)

    def __repr__(self) -> str:  # pragma: no cover
        """For debug purposes."""
        return f"{self.__class__.__name__}(name={self.name!r}, daemon={self.daemon!r}, started={self.started!r}, )"

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
        cdef str name = self.name
        if name is None:
            name = "Threaded: " + getattr(func, "__name__", str(hash(func)))

        # noinspection PyMissingOrEmptyDocstring
        @functools.wraps(prepared)
        def wrapper(*args, **kwargs):  # type: (typing.Any, typing.Any) -> threading.Thread
            thread = threading.Thread(target=prepared, name=name, args=args, kwargs=kwargs, daemon=self.daemon)
            if self.started:
                thread.start()
            return thread

        return wrapper

    def __call__(
        self,
        *args: typing.Union[typing.Callable[..., typing.Union["typing.Awaitable", typing.Any]], typing.Any],
        **kwargs: typing.Any
    ) -> typing.Union[threading.Thread, typing.Callable[..., threading.Thread]]:
        """Executable instance."""
        return super(Threaded, self).__call__(*args, **kwargs)  # type: ignore


def threaded(  # noqa: F811
    name: typing.Optional[typing.Union[str, typing.Callable]] = None, bint daemon: bool = False, bint started: bool = False
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
