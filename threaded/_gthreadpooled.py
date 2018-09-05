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

import typing  # noqa  # pylint: disable=unused-import

import gevent.event  # type: ignore  # noqa  # pylint: disable=unused-import
import gevent.threadpool  # type: ignore  # noqa  # pylint: disable=unused-import
import six

from . import _base_threaded

__all__ = (
    'GThreadPooled',
    'gthreadpooled',
)


class GThreadPooled(_base_threaded.APIPooled):
    """Post function to gevent.threadpool.ThreadPool."""

    __slots__ = ()

    __executor = None  # type: typing.Optional[gevent.threadpool.ThreadPool]

    # pylint: disable=arguments-differ
    @classmethod
    def configure(
        cls,  # type: typing.Type[GThreadPooled]
        max_workers=None,  # type: typing.Optional[int]
        hub=None  # type: typing.Optional[gevent.hub.Hub]
    ):  # type: (...) -> None
        """Pool executor create and configure.

        :param max_workers: Maximum workers
        :type max_workers: typing.Optional[int]
        :param hub: Event-loop hub
        :type hub: typing.Optional[gevent.hub.Hub]
        """
        if max_workers is None:
            max_workers = _base_threaded.cpu_count() * 5

        if isinstance(cls.__executor, gevent.threadpool.ThreadPool):
            if hub is None or hub == cls.__executor.hub:
                if max_workers == cls.__executor.maxsize:
                    return  # Nothing to change)
                cls.__executor.maxsize = max_workers  # We can use internals
                return
            # Hub change. Very special case.
            cls.__executor.kill()  # pragma: no cover

        cls.__executor = gevent.threadpool.ThreadPool(
            maxsize=max_workers,
            hub=hub
        )

    # pylint: enable=arguments-differ

    @classmethod
    def shutdown(cls):  # type: (typing.Type[GThreadPooled]) -> None
        """Shutdown executor.

        Due to not implemented method, set maxsize to 0 (do not accept new).
        """
        if cls.__executor is not None:
            cls.__executor.kill()

    @property
    def executor(self):  # type: () -> gevent.threadpool.ThreadPool
        """Executor instance.

        :rtype: gevent.threadpool.ThreadPool
        """
        if not isinstance(self.__executor, gevent.threadpool.ThreadPool):
            self.configure()
        return self.__executor

    def _get_function_wrapper(
        self,
        func  # type: typing.Callable
    ):  # type: (...) -> typing.Callable[..., gevent.event.AsyncResult]
        """Here should be constructed and returned real decorator.

        :param func: Wrapped function
        :type func: typing.Callable
        :return: wrapped function
        :rtype: typing.Callable[..., gevent.event.AsyncResult]
        """
        # pylint: disable=missing-docstring
        # noinspection PyMissingOrEmptyDocstring
        @six.wraps(func)
        def wrapper(
            *args,  # type: typing.Any
            **kwargs  # type: typing.Any
        ):  # type: (...) -> gevent.event.AsyncResult
            return self.executor.spawn(func, *args, **kwargs)

        # pylint: enable=missing-docstring
        return wrapper

    def __call__(  # pylint: disable=useless-super-delegation
        self,
        *args,  # type: typing.Union[typing.Callable, typing.Any]
        **kwargs  # type: typing.Any
    ):  # type: (...) -> typing.Union[gevent.event.AsyncResult, typing.Callable[..., gevent.event.AsyncResult]]
        """Callable instance."""
        return super(GThreadPooled, self).__call__(*args, **kwargs)


# pylint: disable=unexpected-keyword-arg, no-value-for-parameter
def gthreadpooled(
    func=None  # type: typing.Optional[typing.Callable]
):  # type: (...) -> typing.Union[GThreadPooled, typing.Callable[..., gevent.event.AsyncResult]]
    """Post function to gevent.threadpool.ThreadPool.

    :param func: function to wrap
    :type func: typing.Optional[typing.Callable]
    :rtype: typing.Union[GThreadPooled, typing.Callable[..., gevent.event.AsyncResult]]
    """
    if func is None:
        return GThreadPooled(func=func)
    return GThreadPooled(func=None)(func)
# pylint: enable=unexpected-keyword-arg, no-value-for-parameter
