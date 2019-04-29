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

from __future__ import absolute_import

# Standard Library
import abc
import typing  # noqa  # pylint: disable=unused-import

# External Dependencies
import six

# Local Implementation
from . import class_decorator

__all__ = ("APIPooled", "cpu_count")


try:
    from multiprocessing import cpu_count
except ImportError:

    def cpu_count():  # type: () -> int
        """Fake CPU count."""
        return 1


class APIPooled(six.with_metaclass(abc.ABCMeta, class_decorator.BaseDecorator)):
    """API description for pooled."""

    __slots__ = ()

    __executor = None  # type: typing.Optional[typing.Any]

    @classmethod
    def configure(
        cls,  # type: typing.Type[APIPooled]
        max_workers=None,  # type: typing.Optional[int]
    ):  # type: (...) -> None
        """Pool executor create and configure.

        :param max_workers: Maximum workers
        :type max_workers: typing.Optional[int]
        """
        raise NotImplementedError()  # pragma: no cover

    @classmethod
    def shutdown(cls):  # type: (typing.Type[APIPooled]) -> None
        """Shutdown executor."""
        raise NotImplementedError()  # pragma: no cover

    @property
    def executor(self):  # type: () -> typing.Any
        """Executor instance."""
        raise NotImplementedError()  # pragma: no cover
