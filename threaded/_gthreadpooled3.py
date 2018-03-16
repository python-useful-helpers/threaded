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

"""Python 3 threaded implementation.

Asyncio is supported
"""

import functools
import typing

import gevent.event

from . import _base_gthreadpooled
from . import _py3_helpers

__all__ = (
    'GThreadPooled',
    'gthreadpooled',
)


class GThreadPooled(_base_gthreadpooled.BaseGThreadPooled):
    """Post function to ThreadPoolExecutor."""

    __slots__ = ()

    def _get_function_wrapper(
        self,
        func: typing.Callable
    ) -> typing.Callable[
        ...,
        gevent.event.AsyncResult
    ]:
        """Here should be constructed and returned real decorator.

        :param func: Wrapped function
        :type func: typing.Callable
        :return: wrapped coroutine or function
        :rtype: typing.Callable[..., gevent.event.AsyncResult]
        """
        prepared = _py3_helpers.await_if_required(func)

        # pylint: disable=missing-docstring
        # noinspection PyMissingOrEmptyDocstring
        @functools.wraps(prepared)
        def wrapper(
            *args, **kwargs
        ) -> gevent.event.AsyncResult:
            return self.executor.spawn(prepared, *args, **kwargs)

        # pylint: enable=missing-docstring
        return wrapper


# pylint: disable=unexpected-keyword-arg, no-value-for-parameter
def gthreadpooled(
    func: typing.Optional[typing.Callable] = None
) -> GThreadPooled:
    """Post function to gevent.threadpool.ThreadPool.

    :param func: function to wrap
    :type func: typing.Optional[typing.Callable]
    :rtype: GThreadPooled
    """
    if func is None:
        return GThreadPooled(func=func)
    return GThreadPooled(func=None)(func)
# pylint: enable=unexpected-keyword-arg, no-value-for-parameter
