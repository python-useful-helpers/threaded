#!/usr/bin/env python

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

"""Base class for decorators."""

from __future__ import absolute_import
from __future__ import print_function

# Standard Library
import abc
import functools
import typing  # noqa  # pylint: disable=unused-import

# External Dependencies
import six

__all__ = ("BaseDecorator",)


class BaseDecorator(six.with_metaclass(abc.ABCMeta, object)):
    """Base class for decorators.

    Implements wrapping and __call__, wrapper getter is abstract.

    Note:
        wrapper getter is called only on function call,
        if decorator used without braces.

    Usage example:

    >>> class TestDecorator(BaseDecorator):
    ...     def _get_function_wrapper(self, func):
    ...         print('Wrapping: {}'.format(func.__name__))
    ...         @functools.wraps(func)
    ...         def wrapper(*args, **kwargs):
    ...             print('call_function: {}'.format(func.__name__))
    ...             return func(*args, **kwargs)
    ...         return wrapper

    >>> @TestDecorator
    ... def func_no_init():
    ...     pass
    >>> func_no_init()
    Wrapping: func_no_init
    call_function: func_no_init
    >>> isinstance(func_no_init, TestDecorator)
    True
    >>> func_no_init._func is func_no_init.__wrapped__
    True

    >>> @TestDecorator()
    ... def func_init():
    ...     pass
    Wrapping: func_init
    >>> func_init()
    call_function: func_init
    >>> isinstance(func_init, TestDecorator)
    False
    """

    def __init__(self, func=None):  # type: (typing.Optional[typing.Callable[..., typing.Any]]) -> None
        """Decorator.

        :param func: function to wrap
        :type func: typing.Optional[typing.Callable]
        """
        # noinspection PyArgumentList
        super(BaseDecorator, self).__init__()
        # pylint: disable=assigning-non-slot
        self.__func = func  # type: typing.Optional[typing.Callable[..., typing.Any]]
        if self.__func is not None:
            functools.update_wrapper(self, self.__func)
            self.__wrapped__ = self.__func  # type: typing.Callable[..., typing.Any]
        # pylint: enable=assigning-non-slot

    @property
    def _func(self):  # type: () -> typing.Optional[typing.Callable[..., typing.Any]]
        """Get wrapped function.

        :rtype: typing.Optional[typing.Callable]
        """
        return self.__func  # pragma: no cover

    @abc.abstractmethod
    def _get_function_wrapper(
        self, func
    ):  # type: (typing.Callable[..., typing.Any]) -> typing.Callable[..., typing.Any]
        """Here should be constructed and returned real decorator.

        :param func: Wrapped function
        :type func: typing.Callable
        :rtype: typing.Callable
        """
        raise NotImplementedError()  # pragma: no cover

    def __call__(
        self,
        *args,  # type: typing.Union[typing.Callable[..., typing.Any], typing.Any]
        **kwargs  # type: typing.Any
    ):  # type: (...) -> typing.Any
        """Main decorator getter."""
        l_args = list(args)

        if self._func:
            wrapped = self._func  # type: typing.Callable[..., typing.Any]
        else:
            wrapped = l_args.pop(0)

        wrapper = self._get_function_wrapper(wrapped)
        if self.__func:
            return wrapper(*l_args, **kwargs)
        return wrapper

    def __repr__(self):  # type: () -> str
        """For debug purposes."""
        return "<{cls}({func!r}) at 0x{id:X}>".format(
            cls=self.__class__.__name__, func=self.__func, id=id(self)
        )  # pragma: no cover


# 8<----------------------------------------------------------------------------

if __name__ == "__main__":
    import doctest  # pragma: no cover

    doctest.testmod(verbose=True)  # pragma: no cover
