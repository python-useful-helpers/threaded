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

"""Python 2 pooled implementation.

Uses backport of concurrent.futures.
"""

from __future__ import absolute_import
from __future__ import unicode_literals

import six

from . import _base_pooled

__all__ = (
    'ThreadPooled',
    'ProcessPooled',
)


# pylint: disable=abstract-method
# noinspection PyAbstractClass
class _Py2Pooled(_base_pooled.BasePooled):
    """Python 2 specific base class."""

    def _get_function_wrapper(self, func):
        """Here should be constructed and returned real decorator.

        :param func: Wrapped function
        :type func: typing.Callable
        :return: wrapped function
        :rtype: typing.Callable
        """
        # pylint: disable=missing-docstring
        # noinspection PyMissingOrEmptyDocstring
        @six.wraps(func)
        def wrapper(*args, **kwargs):
            return self.executor.submit(func, *args, **kwargs)
        # pylint: enable=missing-docstring
        return wrapper

# pylint: enable=abstract-method


class ThreadPooled(_Py2Pooled):
    """ThreadPoolExecutor wrapped."""

    __slots__ = ()

    __executor = None

    # pylint: disable=arguments-differ
    @classmethod
    def configure(
        cls,
        max_workers=None,
    ):
        """Pool executor create and configure.

        :param max_workers: Maximum workers
        :type max_workers: typing.Optional[int]
        """
        if isinstance(cls.__executor, _base_pooled.ThreadPoolExecutor):
            if cls.__executor.max_workers == max_workers:
                return
            cls.__executor.shutdown()

        cls.__executor = _base_pooled.ThreadPoolExecutor(
            max_workers=max_workers,
        )

    # pylint: enable=arguments-differ

    @classmethod
    def shutdown(cls):
        """Shutdown executor."""
        if cls.__executor is not None:
            cls.__executor.shutdown()

    @property
    def executor(self):
        """Executor.

        :rtype: _base_pooled.ThreadPoolExecutor
        """
        if not isinstance(
            self.__executor,
            _base_pooled.ThreadPoolExecutor
        ):
            self.configure()
        return self.__executor


class ProcessPooled(_Py2Pooled):
    """ProcessPoolExecutor wrapped."""

    __slots__ = ()

    __executor = None

    @classmethod
    def configure(
        cls,
        max_workers=None,
    ):
        """Pool executor create and configure.

        :param max_workers: Maximum workers
        :type max_workers: typing.Optional[int]
        """
        if isinstance(cls.__executor, _base_pooled.ProcessPoolExecutor):
            if cls.__executor.max_workers == max_workers:
                return
            cls.__executor.shutdown()

        cls.__executor = _base_pooled.ProcessPoolExecutor(
            max_workers=max_workers,
        )

    @classmethod
    def shutdown(cls):
        """Shutdown executor."""
        if cls.__executor is not None:
            cls.__executor.shutdown()

    @property
    def executor(self):
        """Executor.

        :rtype: _base_pooled.ProcessPoolExecutor
        """
        if not isinstance(
            self.__executor,
            _base_pooled.ProcessPoolExecutor
        ):
            self.configure()
        return self.__executor
