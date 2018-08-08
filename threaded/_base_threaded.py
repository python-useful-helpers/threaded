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

"""Base classes for ThreadPooled and Threaded."""

import abc
import concurrent.futures
import typing

from . import _class_decorator


__all__ = (
    'APIPooled',
    'BasePooled',
    'ThreadPoolExecutor',
)


class APIPooled(_class_decorator.BaseDecorator, metaclass=abc.ABCMeta):
    """API description for pooled."""

    __slots__ = ()

    __executor = None  # type: typing.Optional[typing.Any]

    @classmethod
    def configure(
        cls: typing.Type['APIPooled'],
        max_workers: typing.Optional[int] = None,
    ) -> None:
        """Pool executor create and configure.

        :param max_workers: Maximum workers
        :type max_workers: typing.Optional[int]
        """
        raise NotImplementedError()  # pragma: no cover

    @classmethod
    def shutdown(cls: typing.Type['APIPooled']) -> None:
        """Shutdown executor."""
        raise NotImplementedError()  # pragma: no cover

    @property
    def executor(self) -> typing.Any:
        """Executor instance."""
        raise NotImplementedError()  # pragma: no cover


class BasePooled(APIPooled, metaclass=abc.ABCMeta):  # pylint: disable=abstract-method
    """Base ThreadPooled class."""

    __slots__ = ()

    __executor = None  # type: typing.Optional[ThreadPoolExecutor]

    @classmethod
    def configure(
        cls: typing.Type['BasePooled'],
        max_workers: typing.Optional[int] = None,
    ) -> None:
        """Pool executor create and configure.

        :param max_workers: Maximum workers
        :type max_workers: typing.Optional[int]
        """
        if isinstance(cls.__executor, ThreadPoolExecutor):
            if cls.__executor.max_workers == max_workers:
                return
            cls.__executor.shutdown()

        cls.__executor = ThreadPoolExecutor(
            max_workers=max_workers,
        )

    @classmethod
    def shutdown(cls: typing.Type['BasePooled']) -> None:
        """Shutdown executor."""
        if cls.__executor is not None:
            cls.__executor.shutdown()

    @property
    def executor(self) -> 'ThreadPoolExecutor':
        """Executor instance.

        :rtype: ThreadPoolExecutor
        """
        if not isinstance(self.__executor, ThreadPoolExecutor) or self.__executor.is_shutdown:
            self.configure()
        return self.__executor  # type: ignore


class ThreadPoolExecutor(concurrent.futures.ThreadPoolExecutor):
    """Provide readers for protected attributes.

    Simply extend concurrent.futures.ThreadPoolExecutor.
    """

    __slots__ = ()

    @property
    def max_workers(self) -> int:
        """MaxWorkers.

        :rtype: int
        """
        return self._max_workers  # type: ignore

    @property
    def is_shutdown(self) -> bool:
        """Executor shutdown state.

        :rtype: bool
        """
        return self._shutdown  # type: ignore
