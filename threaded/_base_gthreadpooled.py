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

"""gevent.threadpool.ThreadPool usage."""

from __future__ import absolute_import

import gevent.threadpool
import six

from . import _base_threaded

__all__ = (
    'BaseGThreadPooled',
)


class BaseGThreadPooled(_base_threaded.APIPooled):
    """Post function to gevent.threadpool.ThreadPool."""

    __slots__ = ()

    __executor = None

    # pylint: disable=arguments-differ
    @classmethod
    def configure(
        cls,
        max_workers=None,
        hub=None
    ):
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
    def shutdown(cls):
        """Shutdown executor.

        Due to not implemented method, set maxsize to 0 (do not accept new).
        """
        if cls.__executor is not None:
            cls.__executor.kill()

    @property
    def executor(self):
        """Executor instance.

        :rtype: gevent.threadpool.ThreadPool
        """
        if not isinstance(self.__executor, gevent.threadpool.ThreadPool):
            self.configure()
        return self.__executor

    def _get_function_wrapper(self, func):
        """Here should be constructed and returned real decorator.

        :param func: Wrapped function
        :type func: typing.Callable
        :return: wrapped function
        :rtype: typing.Callable[..., gevent.event.AsyncResult]
        """
        # pylint: disable=missing-docstring
        # noinspection PyMissingOrEmptyDocstring
        @six.wraps(func)
        def wrapper(*args, **kwargs):
            return self.executor.spawn(func, *args, **kwargs)
        # pylint: enable=missing-docstring
        return wrapper
