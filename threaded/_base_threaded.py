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
import typing

from . import class_decorator


__all__ = ("APIPooled",)


class APIPooled(class_decorator.BaseDecorator, metaclass=abc.ABCMeta):
    """API description for pooled."""

    __slots__ = ()

    __executor = None  # type: typing.Optional[typing.Any]

    @classmethod
    @abc.abstractmethod
    def configure(cls: typing.Type["APIPooled"], max_workers: typing.Optional[int] = None) -> None:
        """Pool executor create and configure.

        :param max_workers: Maximum workers
        :type max_workers: typing.Optional[int]
        """
        raise NotImplementedError()  # pragma: no cover

    @classmethod
    @abc.abstractmethod
    def shutdown(cls: typing.Type["APIPooled"]) -> None:
        """Shutdown executor."""
        raise NotImplementedError()  # pragma: no cover

    @property
    @abc.abstractmethod
    def executor(self) -> typing.Any:
        """Executor instance."""
        raise NotImplementedError()  # pragma: no cover
