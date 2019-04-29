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

"""Python 2 threaded implementation.

Uses backport of concurrent.futures.
"""

from __future__ import absolute_import

# Standard Library
import threading  # noqa  # pylint: disable=unused-import
import typing  # noqa  # pylint: disable=unused-import

# External Dependencies
import six

# Local Implementation
from . import class_decorator

__all__ = ("Threaded", "threaded")


class Threaded(class_decorator.BaseDecorator):
    """Run function in separate thread."""

    __slots__ = ("__name", "__daemon", "__started")

    def __init__(
        self,
        name=None,  # type: typing.Optional[typing.Union[str, typing.Callable[..., typing.Any]]]
        daemon=False,  # type: bool
        started=False,  # type: bool
    ):  # type: (...) -> None
        """Run function in separate thread.

        :param name: New thread name.
                     If callable: use as wrapped function.
                     If none: use wrapped function name.
        :type name: typing.Optional[typing.Union[str, typing.Callable[..., typing.Any]]]
        :param daemon: Daemonize thread.
        :type daemon: bool
        :param started: Return started thread
        :type started: bool
        """
        # pylint: disable=assigning-non-slot
        self.__daemon = daemon
        self.__started = started
        if callable(name):
            func = name  # type: typing.Optional[typing.Callable[..., typing.Any]]
            self.__name = "Threaded: " + getattr(name, "__name__", str(hash(name)))  # type: str
        else:
            func, self.__name = None, name  # type: ignore
        super(Threaded, self).__init__(func=func)
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

    def __repr__(self):  # type: () -> str  # pragma: no cover
        """For debug purposes."""
        return (
            "{cls}("
            "name={self.name!r}, "
            "daemon={self.daemon!r}, "
            "started={self.started!r}, "
            ")".format(cls=self.__class__.__name__, self=self)
        )  # pragma: no cover

    def _get_function_wrapper(
        self, func
    ):  # type: (typing.Callable[..., typing.Any]) -> typing.Callable[..., threading.Thread]
        """Here should be constructed and returned real decorator.

        :param func: Wrapped function
        :type func: typing.Callable[..., typing.Any]
        :return: wrapped function
        :rtype: typing.Callable[..., threading.Thread]
        """
        name = self.name
        if name is None:
            name = "Threaded: " + getattr(func, "__name__", str(hash(func)))

        # noinspection PyMissingOrEmptyDocstring
        @six.wraps(func)
        def wrapper(  # pylint: disable=missing-docstring
            *args,  # type: typing.Any
            **kwargs  # type: typing.Any
        ):  # type: (...) -> threading.Thread
            thread = threading.Thread(target=func, name=name, args=args, kwargs=kwargs)
            thread.daemon = self.daemon
            if self.started:
                thread.start()
            return thread

        return wrapper

    def __call__(  # pylint: disable=useless-super-delegation
        self,
        *args,  # type: typing.Union[typing.Callable[..., typing.Any], typing.Any]
        **kwargs  # type: typing.Any
    ):  # type: (...) -> typing.Union[threading.Thread, typing.Callable[..., threading.Thread]]
        """Executable instance."""
        return super(Threaded, self).__call__(*args, **kwargs)  # type: ignore


# pylint: disable=unexpected-keyword-arg, no-value-for-parameter
def threaded(
    name=None,  # type: typing.Optional[typing.Union[str, typing.Callable[..., typing.Any]]]
    daemon=False,  # type: bool
    started=False,  # type: bool
):  # type: (...) -> typing.Union[Threaded, typing.Callable[..., threading.Thread]]
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


# pylint: enable=unexpected-keyword-arg, no-value-for-parameter
