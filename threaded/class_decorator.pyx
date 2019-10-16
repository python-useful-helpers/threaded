#    Copyright 2017 - 2019 Alexey Stepanov aka penguinolog
#
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

import asyncio
import functools
import typing


cdef class BaseDecorator:
    """Base class for decorators.

    Implements wrapping and __call__, wrapper getter is abstract.

    .. note:: wrapper getter is called only on function call, if decorator used without braces.
    """

    def __init__(self, func: typing.Optional[typing.Callable] = None) -> None:
        """Decorator.

        :param func: function to wrap
        :type func: typing.Optional[typing.Callable]
        """
        # noinspection PyArgumentList
        super(BaseDecorator, self).__init__()
        # pylint: disable=assigning-non-slot
        self._func = func  # type: typing.Optional[typing.Callable]
        if self._func is not None:
            functools.update_wrapper(self, self._func)
        # pylint: enable=assigning-non-slot

    def _get_function_wrapper(self, func: typing.Callable) -> typing.Callable:
        """Here should be constructed and returned real decorator.

        :param func: Wrapped function
        :type func: typing.Callable
        :rtype: typing.Callable
        """
        raise NotImplementedError()  # pragma: no cover

    def __call__(self, *args: typing.Union[typing.Callable, typing.Any], **kwargs: typing.Any) -> typing.Any:
        """Main decorator getter."""
        cdef list l_args = list(args)

        if self._func:
            wrapped = self._func  # type: typing.Callable
        else:
            wrapped = l_args.pop(0)

        wrapper = self._get_function_wrapper(wrapped)
        if self._func:
            return wrapper(*l_args, **kwargs)
        return wrapper

    def __repr__(self) -> str:
        """For debug purposes."""
        return f"<{self.__class__.__name__}({self._func!r}) at 0x{id(self):X}>"  # pragma: no cover

    @staticmethod
    def _await_if_required(
        target: typing.Callable[..., typing.Union["typing.Awaitable", typing.Any]]
    ) -> typing.Callable[..., typing.Any]:
        """Await result if coroutine was returned."""

        @functools.wraps(target)
        def wrapper(*args, **kwargs):  # type: (typing.Any, typing.Any) -> typing.Any
            """Decorator/wrapper."""
            result = target(*args, **kwargs)
            if asyncio.iscoroutine(result):
                loop = asyncio.new_event_loop()
                result = loop.run_until_complete(result)
                loop.close()
            return result

        return wrapper
