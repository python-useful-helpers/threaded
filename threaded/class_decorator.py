#!/usr/bin/env python

#    Copyright 2017 - 2020 Alexey Stepanov aka penguinolog
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

__all__ = ("BaseDecorator",)

# Standard Library
import abc
import asyncio
import functools
import typing


class BaseDecorator(metaclass=abc.ABCMeta):
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

    def __init__(
        self,
        func: typing.Optional[typing.Callable[..., typing.Union["typing.Awaitable[typing.Any]", typing.Any]]] = None,
    ) -> None:
        """Decorator.

        :param func: function to wrap
        :type func: typing.Optional[typing.Callable]
        """
        # noinspection PyArgumentList
        super().__init__()
        self.__func: typing.Optional[
            typing.Callable[..., typing.Union["typing.Awaitable[typing.Any]", typing.Any]]
        ] = func
        if self.__func is not None:
            functools.update_wrapper(self, self.__func)

    @property
    def _func(self) -> typing.Optional[typing.Callable[..., typing.Union["typing.Awaitable[typing.Any]", typing.Any]]]:
        """Get wrapped function.

        :rtype: typing.Optional[typing.Callable[..., typing.Union[typing.Awaitable, typing.Any]]]
        """
        return self.__func  # pragma: no cover

    @abc.abstractmethod
    def _get_function_wrapper(
        self, func: typing.Callable[..., typing.Union["typing.Awaitable[typing.Any]", typing.Any]]
    ) -> typing.Callable[..., typing.Any]:
        """Here should be constructed and returned real decorator.

        :param func: Wrapped function
        :type func: typing.Callable[..., typing.Union[typing.Awaitable, typing.Any]]
        :rtype: typing.Callable
        """
        raise NotImplementedError()  # pragma: no cover

    def __call__(
        self,
        *args: typing.Union[typing.Callable[..., typing.Union["typing.Awaitable[typing.Any]", typing.Any]], typing.Any],
        **kwargs: typing.Any,
    ) -> typing.Any:
        """Main decorator getter.

        :return: result of decorated function or result getter
        :rtype: Any
        """
        l_args: typing.List[typing.Any] = list(args)

        if self._func:
            wrapped: typing.Callable[..., typing.Union["typing.Awaitable[typing.Any]", typing.Any]] = self._func
        else:
            wrapped = l_args.pop(0)

        wrapper: typing.Callable[..., typing.Any] = self._get_function_wrapper(wrapped)
        if self.__func:
            return wrapper(*l_args, **kwargs)
        return wrapper

    @staticmethod
    def _await_if_required(
        target: typing.Callable[..., typing.Union["typing.Awaitable[typing.Any]", typing.Any]]
    ) -> typing.Callable[..., typing.Any]:
        """Await result if coroutine was returned.

        :return: function, which will await for result if it's required
        :rtype: Callable[..., Any]
        """

        @functools.wraps(target)
        def wrapper(*args: typing.Any, **kwargs: typing.Any) -> typing.Any:
            """Decorator/wrapper.

            :return: target execution result (awaited if needed)
            :rtype: Any
            """
            result = target(*args, **kwargs)
            if asyncio.iscoroutine(result):
                loop = asyncio.new_event_loop()
                result = loop.run_until_complete(result)
                loop.close()
            return result

        return wrapper

    def __repr__(self) -> str:
        """For debug purposes.

        :return: repr info
        :rtype: str
        """
        return f"<{self.__class__.__name__}({self.__func!r}) at 0x{id(self):X}>"  # pragma: no cover


# 8<----------------------------------------------------------------------------

if __name__ == "__main__":
    # Standard Library
    import doctest  # pragma: no cover

    doctest.testmod(verbose=True)  # pragma: no cover
