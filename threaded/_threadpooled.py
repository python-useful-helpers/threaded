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
# noinspection PyCompatibility
import concurrent.futures
import typing  # noqa  # pylint: disable=unused-import

# External Dependencies
import six

# Local Implementation
from . import _base_threaded

__all__ = ("ThreadPooled", "threadpooled")


class ThreadPooled(_base_threaded.APIPooled):
    """Post function to ThreadPoolExecutor."""

    __slots__ = ()

    __executor = None  # type: typing.Optional[ThreadPoolExecutor]

    @classmethod
    def configure(
        cls,  # type: typing.Type[ThreadPooled]
        max_workers=None,  # type: typing.Optional[int]
    ):  # type: (...) -> None
        """Pool executor create and configure.

        :param max_workers: Maximum workers
        :type max_workers: typing.Optional[int]
        """
        if isinstance(cls.__executor, ThreadPoolExecutor):
            if cls.__executor.max_workers == max_workers:
                return
            cls.__executor.shutdown()

        cls.__executor = ThreadPoolExecutor(max_workers=max_workers)

    @classmethod
    def shutdown(cls):  # type: (typing.Type[ThreadPooled]) -> None
        """Shutdown executor."""
        if cls.__executor is not None:
            cls.__executor.shutdown()

    @property
    def executor(self):  # type: () -> ThreadPoolExecutor
        """Executor instance.

        :rtype: ThreadPoolExecutor
        """
        if not isinstance(self.__executor, ThreadPoolExecutor) or self.__executor.is_shutdown:
            self.configure()
        return self.__executor  # type: ignore

    def _get_function_wrapper(
        self, func
    ):  # type: (typing.Callable[..., typing.Any]) -> typing.Callable[..., concurrent.futures.Future[typing.Any]]
        """Here should be constructed and returned real decorator.

        :param func: Wrapped function
        :type func: typing.Callable
        :return: wrapped function
        :rtype: typing.Callable[..., concurrent.futures.Future]
        """
        # noinspection PyMissingOrEmptyDocstring
        @six.wraps(func)
        def wrapper(  # pylint: disable=missing-docstring
            *args,  # type: typing.Any
            **kwargs  # type: typing.Any
        ):  # type: (...) -> concurrent.futures.Future[typing.Any]
            return self.executor.submit(func, *args, **kwargs)

        return wrapper


# pylint: disable=unexpected-keyword-arg, no-value-for-parameter
def threadpooled(
    func=None  # type: typing.Optional[typing.Callable[..., typing.Any]]
):  # type: (...) -> typing.Union[ThreadPooled, typing.Callable[..., concurrent.futures.Future[typing.Any]]]
    """Post function to ThreadPoolExecutor.

    :param func: function to wrap
    :type func: typing.Optional[typing.Callable[..., typing.Any]]
    :return: ThreadPooled instance, if called as function or argumented decorator, else callable wrapper
    :rtype: typing.Union[ThreadPooled, typing.Callable[..., concurrent.futures.Future]]
    """
    if func is None:
        return ThreadPooled(func=func)
    return ThreadPooled(func=None)(func)  # type: ignore


# pylint: enable=unexpected-keyword-arg, no-value-for-parameter


class ThreadPoolExecutor(concurrent.futures.ThreadPoolExecutor):
    """Provide readers for protected attributes.

    Simply extend concurrent.futures.ThreadPoolExecutor.
    """

    __slots__ = ()

    def __init__(
        self, max_workers=None
    ):  # type: (typing.Optional[int]) -> None
        """Override init due to difference between Python <3.5 and 3.5+.

        :param max_workers: Maximum workers allowed. If none: cpu_count() or 1) * 5
        :type max_workers: typing.Optional[int]
        """
        if max_workers is None:  # Use 3.5+ behavior
            max_workers = (_base_threaded.cpu_count() or 1) * 5
        super(ThreadPoolExecutor, self).__init__(max_workers=max_workers)

    @property
    def max_workers(self):  # type: () -> int
        """MaxWorkers.

        :rtype: int
        """
        return self._max_workers  # type: ignore

    @property
    def is_shutdown(self):  # type: () -> bool
        """Executor shutdown state.

        :rtype: bool
        """
        return self._shutdown  # type: ignore
