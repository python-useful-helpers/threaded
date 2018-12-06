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

"""AsyncIOTask implementation."""

import asyncio
import functools
import typing

from . import class_decorator

__all__ = ("AsyncIOTask", "asynciotask")


class AsyncIOTask(class_decorator.BaseDecorator):
    """Wrap to asyncio.Task."""

    __slots__ = ("__loop_getter", "__loop_getter_need_context")

    def __init__(
        self,
        func: typing.Optional[typing.Callable[..., "typing.Awaitable"]] = None,
        *,
        loop_getter: typing.Union[
            typing.Callable[..., asyncio.AbstractEventLoop], asyncio.AbstractEventLoop
        ] = asyncio.get_event_loop,
        loop_getter_need_context: bool = False
    ) -> None:
        """Wrap function in future and return.

        :param func: Function to wrap
        :type func: typing.Optional[typing.Callable[..., typing.Awaitable]]
        :param loop_getter: Method to get event loop, if wrap in asyncio task
        :type loop_getter: typing.Union[
                               typing.Callable[..., asyncio.AbstractEventLoop],
                               asyncio.AbstractEventLoop
                           ]
        :param loop_getter_need_context: Loop getter requires function context
        :type loop_getter_need_context: bool
        """
        super(AsyncIOTask, self).__init__(func=func)
        self.__loop_getter = loop_getter
        self.__loop_getter_need_context = loop_getter_need_context

    @property
    def loop_getter(self) -> typing.Union[typing.Callable[..., asyncio.AbstractEventLoop], asyncio.AbstractEventLoop]:
        """Loop getter.

        :rtype: typing.Union[typing.Callable[..., asyncio.AbstractEventLoop], asyncio.AbstractEventLoop]
        """
        return self.__loop_getter

    @property
    def loop_getter_need_context(self) -> bool:
        """Loop getter need execution context.

        :rtype: bool
        """
        return self.__loop_getter_need_context

    def get_loop(self, *args, **kwargs):  # type: (typing.Any, typing.Any) -> asyncio.AbstractEventLoop
        """Get event loop in decorator class."""
        if callable(self.loop_getter):
            if self.loop_getter_need_context:
                return self.loop_getter(*args, **kwargs)  # pylint: disable=not-callable
            return self.loop_getter()  # pylint: disable=not-callable
        return self.loop_getter

    def _get_function_wrapper(
        self, func: typing.Callable[..., "typing.Awaitable"]
    ) -> typing.Callable[..., asyncio.Task]:
        """Here should be constructed and returned real decorator.

        :param func: Wrapped function
        :type func: typing.Callable[..., typing.Awaitable]
        :return: wrapper, which will produce asyncio.Task on call with function called inside it
        :rtype: typing.Callable[..., asyncio.Task]
        """
        # noinspection PyMissingOrEmptyDocstring
        @functools.wraps(func)  # pylint: disable=missing-docstring
        def wrapper(*args, **kwargs):  # type: (typing.Any, typing.Any) -> asyncio.Task
            loop = self.get_loop(*args, **kwargs)
            return loop.create_task(func(*args, **kwargs))

        return wrapper

    def __call__(  # pylint: disable=useless-super-delegation
        self, *args: typing.Union[typing.Callable[..., "typing.Awaitable"], typing.Any], **kwargs: typing.Any
    ) -> typing.Union[asyncio.Task, typing.Callable[..., asyncio.Task]]:
        """Callable instance."""
        return super(AsyncIOTask, self).__call__(*args, **kwargs)  # type: ignore

    def __repr__(self) -> str:
        """For debug purposes."""
        return (
            "<{cls}("
            "{func!r}, "
            "loop_getter={self.loop_getter!r}, "
            "loop_getter_need_context={self.loop_getter_need_context!r}, "
            ") at 0x{id:X}>".format(cls=self.__class__.__name__, func=self._func, self=self, id=id(self))
        )  # pragma: no cover


# pylint: disable=function-redefined, unused-argument
@typing.overload
def asynciotask(
    func: None = None,
    *,
    loop_getter: typing.Union[
        typing.Callable[..., asyncio.AbstractEventLoop], asyncio.AbstractEventLoop
    ] = asyncio.get_event_loop,
    loop_getter_need_context: bool = False
) -> AsyncIOTask:
    """Overload: no function."""


@typing.overload  # noqa: F811
def asynciotask(
    func: typing.Callable[..., "typing.Awaitable"],
    *,
    loop_getter: typing.Union[
        typing.Callable[..., asyncio.AbstractEventLoop], asyncio.AbstractEventLoop
    ] = asyncio.get_event_loop,
    loop_getter_need_context: bool = False
) -> typing.Callable[..., asyncio.Task]:
    """Overload: provided function."""


# pylint: enable=unused-argument
def asynciotask(  # noqa: F811
    func: typing.Optional[typing.Callable[..., "typing.Awaitable"]] = None,
    *,
    loop_getter: typing.Union[
        typing.Callable[..., asyncio.AbstractEventLoop], asyncio.AbstractEventLoop
    ] = asyncio.get_event_loop,
    loop_getter_need_context: bool = False
) -> typing.Union[AsyncIOTask, typing.Callable[..., asyncio.Task]]:
    """Wrap function in future and return.

    :param func: Function to wrap
    :type func: typing.Optional[typing.Callable[..., typing.Awaitable]]
    :param loop_getter: Method to get event loop, if wrap in asyncio task
    :type loop_getter: typing.Union[
                           typing.Callable[..., asyncio.AbstractEventLoop],
                           asyncio.AbstractEventLoop
                       ]
    :param loop_getter_need_context: Loop getter requires function context
    :type loop_getter_need_context: bool
    :return: AsyncIOTask instance, if called as function or argumented decorator, else callable wrapper
    :rtype: typing.Union[AsyncIOTask, typing.Callable[..., asyncio.Task]]
    """
    if func is None:
        return AsyncIOTask(func=func, loop_getter=loop_getter, loop_getter_need_context=loop_getter_need_context)
    return AsyncIOTask(  # type: ignore
        func=None, loop_getter=loop_getter, loop_getter_need_context=loop_getter_need_context
    )(func)


# pylint: enable=function-redefined
