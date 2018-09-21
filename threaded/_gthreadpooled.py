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

"""Python 3 threaded implementation.

Asyncio is supported
"""

import functools
import os
import typing

import gevent.event  # type: ignore
import gevent.threadpool  # type: ignore

from . import _base_threaded

__all__ = ("GThreadPooled", "gthreadpooled")


class GThreadPooled(_base_threaded.APIPooled):
    """Post function to ThreadPoolExecutor."""

    __slots__ = ()

    __executor = None  # type: typing.Optional[gevent.threadpool.ThreadPool]

    @classmethod
    def configure(  # pylint: disable=arguments-differ
        cls: typing.Type["GThreadPooled"],
        max_workers: typing.Optional[int] = None,
        hub: typing.Optional[gevent.hub.Hub] = None,
    ) -> None:
        """Pool executor create and configure.

        :param max_workers: Maximum workers
        :type max_workers: typing.Optional[int]
        :param hub: Event-loop hub
        :type hub: typing.Optional[gevent.hub.Hub]
        """
        if max_workers is None:
            max_workers = os.cpu_count() * 5  # type: ignore

        if isinstance(cls.__executor, gevent.threadpool.ThreadPool):
            if hub is None or hub == cls.__executor.hub:
                if max_workers == cls.__executor.maxsize:
                    return  # Nothing to change)
                cls.__executor.maxsize = max_workers  # We can use internals
                return
            # Hub change. Very special case.
            cls.__executor.kill()  # pragma: no cover

        cls.__executor = gevent.threadpool.ThreadPool(maxsize=max_workers, hub=hub)

    @classmethod
    def shutdown(cls: typing.Type["GThreadPooled"]) -> None:
        """Shutdown executor.

        Due to not implemented method, set maxsize to 0 (do not accept new).
        """
        if cls.__executor is not None:
            cls.__executor.kill()

    @property
    def executor(self) -> gevent.threadpool.ThreadPool:
        """Executor instance.

        :rtype: gevent.threadpool.ThreadPool
        """
        if not isinstance(self.__executor, gevent.threadpool.ThreadPool):
            self.configure()
        return self.__executor

    def _get_function_wrapper(
        self, func: typing.Callable[..., typing.Union["typing.Awaitable", typing.Any]]
    ) -> typing.Callable[..., gevent.event.AsyncResult]:
        """Here should be constructed and returned real decorator.

        :param func: Wrapped function
        :type func: typing.Callable[..., typing.Union[typing.Awaitable, typing.Any]
        :return: wrapped coroutine or function
        :rtype: typing.Callable[..., gevent.event.AsyncResult]
        """
        prepared = self._await_if_required(func)

        # noinspection PyMissingOrEmptyDocstring
        @functools.wraps(prepared)  # pylint: disable=missing-docstring
        def wrapper(*args, **kwargs):  # type: (typing.Any, typing.Any) -> gevent.event.AsyncResult
            return self.executor.spawn(prepared, *args, **kwargs)

        return wrapper

    def __call__(  # pylint: disable=useless-super-delegation
        self,
        *args: typing.Union[typing.Callable[..., typing.Union["typing.Awaitable", typing.Any]], typing.Any],
        **kwargs: typing.Any
    ) -> typing.Union[gevent.event.AsyncResult, typing.Callable[..., gevent.event.AsyncResult]]:
        """Callable instance."""
        return super(GThreadPooled, self).__call__(*args, **kwargs)


# pylint: disable=function-redefined, unused-argument
@typing.overload
def gthreadpooled(
    func: typing.Callable[..., typing.Union["typing.Awaitable", typing.Any]]
) -> typing.Callable[..., gevent.event.AsyncResult]:
    """Overloaded: func provided."""
    pass  # pragma: no cover


@typing.overload  # noqa: F811
def gthreadpooled(func: None = None) -> GThreadPooled:
    """Overloaded: Func is None."""
    pass  # pragma: no cover


# pylint: enable=unused-argument
def gthreadpooled(  # noqa: F811
    func: typing.Optional[typing.Callable[..., typing.Union["typing.Awaitable", typing.Any]]] = None
) -> typing.Union[GThreadPooled, typing.Callable[..., gevent.event.AsyncResult]]:
    """Post function to gevent.threadpool.ThreadPool.

    :param func: function to wrap
    :type func: typing.Optional[typing.Callable]
    :return: GThreadPooled instance, if called as function or argumented decorator, else callable wrapper
    :rtype: typing.Union[GThreadPooled, typing.Callable[..., gevent.event.AsyncResult]]
    """
    if func is None:
        return GThreadPooled(func=func)
    return GThreadPooled(func=None)(func)


# pylint: enable=function-redefined
