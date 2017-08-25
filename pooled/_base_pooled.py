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

"""Base class for pooled."""

from __future__ import absolute_import
from __future__ import unicode_literals

import abc
# noinspection PyCompatibility
import concurrent.futures
import functools
import os
import typing

import six

__all__ = (
    'BasePooled',
    'ThreadPoolExecutor',
    'ProcessPoolExecutor',
)


class BasePooled(
    type.__new__(
        abc.ABCMeta,
        'BasePooled' if six.PY3 else b'BasePooled',
        (typing.Callable, ),
        {}
    )
):
    """Base pooled class."""

    __slots__ = (
        '__func',
        '__wrapped__',
    )

    @classmethod
    @abc.abstractmethod
    def configure(
        cls,
        max_workers=None,
    ):
        """Pool executor create and configure.

        :param max_workers: Maximum workers
        :type max_workers: typing.Optional[int]
        """
        raise NotImplementedError("configure is not implemented")

    @classmethod
    @abc.abstractmethod
    def shutdown(cls):
        """Shutdown executor."""
        raise NotImplementedError("shutdown is not implemented")

    @property
    @abc.abstractmethod
    def executor(self):
        """Executor instance."""
        raise NotImplementedError("executor getter is not implemented")

    def __init__(self, func=None):
        """Pooled decorator.

        :param func: function to wrap
        :type func: typing.Callable[]
        """
        # pylint: disable=assigning-non-slot
        self.__func = func
        if self.__func is not None:
            functools.update_wrapper(self, self.__func)
            if not six.PY34:
                self.__wrapped__ = self.__func
        # pylint: enable=assigning-non-slot
        # noinspection PyArgumentList
        super(BasePooled, self).__init__()

    @abc.abstractmethod
    def _get_function_wrapper(self, func):
        """Here should be constructed and returned real decorator.

        :param func: Wrapped function
        :type func: typing.Callable
        :rtype: typing.Callable
        """
        raise NotImplementedError()

    def __call__(self, *args, **kwargs):
        """Main decorator getter.

        :returns: Decorated function. On python 3.3+ asyncio.Task is supported.
        :rtype: typing.Union[typing.Callable, concurrent.futures.Future]
        """
        args = list(args)
        wrapped = self.__func or args.pop(0)
        wrapper = self._get_function_wrapper(wrapped)
        if self.__func:
            return wrapper(*args, **kwargs)
        return wrapper

    def __repr__(self):
        """For debug purposes."""
        return "<{cls}({func!r}) at 0x{id:X}>".format(
            cls=self.__class__.__name__,
            func=self.__func,
            id=id(self)
        )


class ThreadPoolExecutor(concurrent.futures.ThreadPoolExecutor):
    """Readers for protected attributes."""

    __slots__ = ()

    def __init__(self, max_workers=None):
        """Override init due to difference between Python <3.5 and 3.5+."""
        if max_workers is None:  # Use 3.5+ behavior
            max_workers = (os.cpu_count() or 1) * 5
        super(
            ThreadPoolExecutor,
            self
        ).__init__(
            max_workers=max_workers,
        )

    @property
    def max_workers(self):
        """MaxWorkers.

        :rtype: int
        """
        return self._max_workers


class ProcessPoolExecutor(concurrent.futures.ProcessPoolExecutor):
    """Readers for protected attributes."""

    __slots__ = ()

    def __init__(self, max_workers=None):
        """Override init due to difference between Python <3.5 and 3.5+."""
        if max_workers is None:  # Use 3.5+ behavior
            max_workers = (os.cpu_count() or 1) * 5
        super(
            ProcessPoolExecutor,
            self
        ).__init__(
            max_workers=max_workers,
        )

    @property
    def max_workers(self):
        """MaxWorkers.

        :rtype: int
        """
        return self._max_workers
