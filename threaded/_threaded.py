#    Copyright 2017 - 2020 Alexey Stepanov aka penguinolog
##
#    Licensed under the Apache License, Version 2.0 (the "License"); you may
#    not use this file except in compliance with the License. You may obtain
#    a copy of the License at

#         http://www.apache.org/licenses/LICENSE-2.0

#    Unless required by applicable law or agreed to in writing, software
#    distributed under the License is distributed on an "AS IS" BASIS, WITHOUT
#    WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the
#    License for the specific language governing permissions and limitations
#    under the License.

"""Threaded implementation.

Asyncio is supported
"""

from __future__ import annotations

# Standard Library
import functools
import threading
import typing

# Local Implementation
from . import class_decorator

if typing.TYPE_CHECKING:
    from collections.abc import Awaitable
    from collections.abc import Callable

    from typing_extensions import ParamSpec

    Spec = ParamSpec("Spec")

__all__ = ("Threaded", "threaded")


class Threaded(class_decorator.BaseDecorator):
    """Run function in separate thread."""

    __slots__ = ("__name", "__daemon", "__started")

    def __init__(
        self,
        name: None | (str | Callable[..., Awaitable[typing.Any] | typing.Any]) = None,
        daemon: bool = False,
        started: bool = False,
    ) -> None:
        """Run function in separate thread.

        :param name: New thread name.
                     If callable: use as wrapped function.
                     If none: use wrapped function name.
        :type name: typing.Optional[typing.Union[str, Callable[..., typing.Union[Awaitable, typing.Any]]]]
        :param daemon: Daemonize thread.
        :type daemon: bool
        :param started: Return started thread
        :type started: bool
        """
        self.__daemon: bool = daemon
        self.__started: bool = started
        if callable(name):
            func: Callable[..., Awaitable[typing.Any] | typing.Any] | None = name
            self.__name: str | None = "Threaded: " + getattr(name, "__name__", str(hash(name)))
        else:
            func, self.__name = None, name
        super().__init__(func=func)

    @property
    def name(self) -> str | None:
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

    def __repr__(self) -> str:  # pragma: no cover
        """For debug purposes.

        :return: repr data
        :rtype: str
        """
        return f"{self.__class__.__name__}(name={self.name!r}, daemon={self.daemon!r}, started={self.started!r}, )"

    def _get_function_wrapper(
        self, func: Callable[Spec, Awaitable[typing.Any] | typing.Any]
    ) -> Callable[..., threading.Thread]:
        """Here should be constructed and returned real decorator.

        :param func: Wrapped function
        :type func: Callable[..., typing.Union[Awaitable, typing.Any]]
        :return: wrapped function
        :rtype: Callable[..., threading.Thread]
        """
        prepared: Callable[Spec, typing.Any] = self._await_if_required(func)
        name: str | None = self.name
        if name is None:
            name = "Threaded: " + getattr(func, "__name__", str(hash(func)))

        # noinspection PyMissingOrEmptyDocstring
        @functools.wraps(prepared)
        def wrapper(*args: Spec.args, **kwargs: Spec.kwargs) -> threading.Thread:
            """Thread getter.

            :return: Thread object
            :rtype: threading.Thread
            """
            thread = threading.Thread(target=prepared, name=name, args=args, kwargs=kwargs, daemon=self.daemon)
            if self.started:
                thread.start()
            return thread

        return wrapper

    def __call__(
        self,
        *args: Callable[..., Awaitable[typing.Any] | typing.Any] | typing.Any,
        **kwargs: typing.Any,
    ) -> threading.Thread | Callable[..., threading.Thread]:
        """Executable instance.

        :return: Thread object or Thread getter
        :rtype: Union[threading.Thread, Callable[..., threading.Thread]]
        """
        return super().__call__(*args, **kwargs)  # type: ignore[no-any-return]


@typing.overload
def threaded(
    name: Callable[..., typing.Any], daemon: bool = False, started: bool = False
) -> Callable[..., threading.Thread]:
    """Overload: Call decorator without arguments."""


@typing.overload
def threaded(name: str | None = None, daemon: bool = False, started: bool = False) -> Threaded:
    """Overload: Name is not callable."""


def threaded(
    name: str | Callable[..., typing.Any] | None = None,
    daemon: bool = False,
    started: bool = False,
) -> Threaded | Callable[..., threading.Thread]:
    """Run function in separate thread.

    :param name: New thread name.
                 If callable: use as wrapped function.
                 If none: use wrapped function name.
    :type name: typing.Union[None, str, Callable]
    :param daemon: Daemonize thread.
    :type daemon: bool
    :param started: Return started thread
    :type started: bool
    :return: Threaded instance, if called as function or argumented decorator, else callable wrapper
    :rtype: typing.Union[Threaded, Callable[..., threading.Thread]]
    """
    if callable(name):
        func, name = (name, "Threaded: " + getattr(name, "__name__", str(hash(name))))
        return Threaded(
            name=name,
            daemon=daemon,
            started=started,
        )(
            func
        )  # type: ignore[return-value]
    return Threaded(name=name, daemon=daemon, started=started)
