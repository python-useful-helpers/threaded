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

"""Python 3 threaded implementation.

Asyncio is supported
"""

# noinspection PyCompatibility
import asyncio
# noinspection PyCompatibility
import concurrent.futures
import functools
import threading
import typing

import six

from . import _base_threaded
from . import _class_decorator
from . import _py3_helpers

__all__ = (
    'ThreadPooled',
    'Threaded',
    'AsyncIOTask',
    'threadpooled',
    'threaded',
    'asynciotask',
)


class ThreadPooled(_base_threaded.BasePooled):
    """Post function to ThreadPoolExecutor."""

    __slots__ = (
        '__loop_getter',
        '__loop_getter_need_context'
    )

    def __init__(
        self,
        func: typing.Optional[typing.Callable] = None,
        *,
        loop_getter: typing.Union[
            None,
            typing.Callable[..., asyncio.AbstractEventLoop],
            asyncio.AbstractEventLoop
        ]=None,
        loop_getter_need_context: bool = False
    ):
        """Wrap function in future and return.

        :param func: function to wrap
        :type func: typing.Optional[typing.Callable]
        :param loop_getter: Method to get event loop, if wrap in asyncio task
        :type loop_getter: typing.Union[
                               None,
                               typing.Callable[..., asyncio.AbstractEventLoop],
                               asyncio.AbstractEventLoop
                           ]
        :param loop_getter_need_context: Loop getter requires function context
        :type loop_getter_need_context: bool
        """
        super(ThreadPooled, self).__init__(func=func)
        self.__loop_getter = loop_getter
        self.__loop_getter_need_context = loop_getter_need_context

    @property
    def loop_getter(
        self
    ) -> typing.Union[
        None,
        typing.Callable[..., asyncio.AbstractEventLoop],
        asyncio.AbstractEventLoop
    ]:
        """Loop getter.

        :rtype: typing.Union[
                    None,
                    typing.Callable[..., asyncio.AbstractEventLoop],
                    asyncio.AbstractEventLoop
                ]
        """
        return self.__loop_getter

    @property
    def loop_getter_need_context(self) -> bool:
        """Loop getter need execution context.

        :rtype: bool
        """
        return self.__loop_getter_need_context

    def _get_function_wrapper(
        self,
        func: typing.Callable
    ) -> typing.Callable[
        ...,
        typing.Union[
            concurrent.futures.Future,
            asyncio.Task
        ]
    ]:
        """Here should be constructed and returned real decorator.

        :param func: Wrapped function
        :type func: typing.Callable
        :return: wrapped coroutine or function
        :rtype: typing.Callable[
                    ...,
                    typing.Union[
                        concurrent.futures.Future,
                        asyncio.Task
                    ]
                ]
        """
        prepared = _py3_helpers.await_if_required(func)

        # pylint: disable=missing-docstring
        # noinspection PyMissingOrEmptyDocstring
        @functools.wraps(prepared)
        def wrapper(
            *args, **kwargs
        ) -> typing.Union[
            concurrent.futures.Future,
            asyncio.Task
        ]:
            loop = _py3_helpers.get_loop(self, *args, **kwargs)

            if loop is None:
                return self.executor.submit(prepared, *args, **kwargs)

            return loop.run_in_executor(
                self.executor,
                functools.partial(
                    prepared,
                    *args, **kwargs
                )
            )

        # pylint: enable=missing-docstring
        return wrapper

    def __repr__(self) -> str:
        """For debug purposes."""
        return (
            "<{cls}("
            "{func!r}, "
            "loop_getter={self.loop_getter!r}, "
            "loop_getter_need_context={self.loop_getter_need_context!r}, "
            ") at 0x{id:X}>".format(
                cls=self.__class__.__name__,
                func=self._func,
                self=self,
                id=id(self)
            )
        )  # pragma: no cover


class Threaded(_base_threaded.BaseThreaded):
    """Run function in separate thread."""

    __slots__ = ()

    def _get_function_wrapper(
        self,
        func: typing.Callable
    ) -> typing.Callable[..., threading.Thread]:
        """Here should be constructed and returned real decorator.

        :param func: Wrapped function
        :type func: typing.Callable
        :return: wrapped function
        :rtype: typing.Callable[..., threading.Thread]
        """
        prepared = _py3_helpers.await_if_required(func)
        name = self.name
        if name is None:
            name = 'Threaded: ' + getattr(
                func,
                '__name__',
                str(hash(func))
            )

        # pylint: disable=missing-docstring
        # noinspection PyMissingOrEmptyDocstring
        @six.wraps(prepared)
        def wrapper(*args, **kwargs) -> threading.Thread:
            thread = threading.Thread(
                target=prepared,
                name=name,
                args=args,
                kwargs=kwargs,
                daemon=self.daemon
            )
            if self.started:
                thread.start()
            return thread

        # pylint: enable=missing-docstring
        return wrapper


class AsyncIOTask(_class_decorator.BaseDecorator):
    """Wrap to asyncio.Task."""

    __slots__ = (
        '__loop_getter',
        '__loop_getter_need_context',
    )

    def __init__(
        self,
        func: typing.Optional[typing.Callable] = None,
        *,
        loop_getter: typing.Union[
            typing.Callable[..., asyncio.AbstractEventLoop],
            asyncio.AbstractEventLoop
        ]=asyncio.get_event_loop,
        loop_getter_need_context: bool = False
    ):
        """Wrap function in future and return.

        :param func: Function to wrap
        :type func: typing.Optional[typing.Callable]
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
    def loop_getter(
            self
    ) -> typing.Union[
        typing.Callable[..., asyncio.AbstractEventLoop],
        asyncio.AbstractEventLoop
    ]:
        """Loop getter.

        :rtype: typing.Union[
                    typing.Callable[..., asyncio.AbstractEventLoop],
                    asyncio.AbstractEventLoop
                ]
        """
        return self.__loop_getter

    @property
    def loop_getter_need_context(self) -> bool:
        """Loop getter need execution context.

        :rtype: bool
        """
        return self.__loop_getter_need_context

    def _get_function_wrapper(
        self,
        func: typing.Callable
    ) -> typing.Callable[..., asyncio.Task]:
        """Here should be constructed and returned real decorator.

        :param func: Wrapped function
        :type func: typing.Callable
        :rtype: typing.Callable[..., asyncio.Task]
        """
        # pylint: disable=missing-docstring
        # noinspection PyCompatibility,PyMissingOrEmptyDocstring
        @functools.wraps(func)
        def wrapper(*args, **kwargs) -> asyncio.Task:
            loop = _py3_helpers.get_loop(self, *args, **kwargs)
            return loop.create_task(func(*args, **kwargs))

        # pylint: enable=missing-docstring
        return wrapper

    def __repr__(self):
        """For debug purposes."""
        return (
            "<{cls}("
            "{func!r}, "
            "loop_getter={self.loop_getter!r}, "
            "loop_getter_need_context={self.loop_getter_need_context!r}, "
            ") at 0x{id:X}>".format(
                cls=self.__class__.__name__,
                func=self._func,
                self=self,
                id=id(self)
            )
        )  # pragma: no cover


# pylint: disable=unexpected-keyword-arg, no-value-for-parameter
def threadpooled(
    func: typing.Optional[typing.Callable] = None,
    *,
    loop_getter: typing.Union[
        None,
        typing.Callable[..., asyncio.AbstractEventLoop],
        asyncio.AbstractEventLoop
    ]=None,
    loop_getter_need_context: bool = False
) -> ThreadPooled:
    """Post function to ThreadPoolExecutor.

    :param func: function to wrap
    :type func: typing.Optional[typing.Callable]
    :param loop_getter: Method to get event loop, if wrap in asyncio task
    :type loop_getter: typing.Union[
                           None,
                           typing.Callable[..., asyncio.AbstractEventLoop],
                           asyncio.AbstractEventLoop
                       ]
    :param loop_getter_need_context: Loop getter requires function context
    :type loop_getter_need_context: bool
    :rtype: ThreadPooled
    """
    if func is None:
        return ThreadPooled(
            func=func,
            loop_getter=loop_getter,
            loop_getter_need_context=loop_getter_need_context
        )
    return ThreadPooled(
        func=None,
        loop_getter=loop_getter,
        loop_getter_need_context=loop_getter_need_context
    )(func)


def threaded(
    name: typing.Union[None, str, typing.Callable] = None,
    daemon: bool = False,
    started: bool = False
) -> Threaded:
    """Run function in separate thread.

    :param name: New thread name.
                 If callable: use as wrapped function.
                 If none: use wrapped function name.
    :type name: typing.Union[None, str, typing.Callable]
    :param daemon: Daemonize thread.
    :type daemon: bool
    :param started: Return started thread
    :type started: bool
    :rtype: Threaded
    """
    if callable(name):
        func, name = (
            name,
            'Threaded: ' + getattr(name, '__name__', str(hash(name)))
        )
        return Threaded(name=name, daemon=daemon, started=started)(func)
    return Threaded(name=name, daemon=daemon, started=started)


def asynciotask(
    func: typing.Optional[typing.Callable] = None,
    *,
    loop_getter: typing.Union[
        typing.Callable[..., asyncio.AbstractEventLoop],
        asyncio.AbstractEventLoop
    ]=asyncio.get_event_loop,
    loop_getter_need_context: bool = False
) -> AsyncIOTask:
    """Wrap function in future and return.

    :param func: Function to wrap
    :type func: typing.Optional[typing.Callable]
    :param loop_getter: Method to get event loop, if wrap in asyncio task
    :type loop_getter: typing.Union[
                           typing.Callable[..., asyncio.AbstractEventLoop],
                           asyncio.AbstractEventLoop
                       ]
    :param loop_getter_need_context: Loop getter requires function context
    :type loop_getter_need_context: bool
    """
    if func is None:
        return AsyncIOTask(
            func=func,
            loop_getter=loop_getter,
            loop_getter_need_context=loop_getter_need_context
        )
    return AsyncIOTask(
        func=None,
        loop_getter=loop_getter,
        loop_getter_need_context=loop_getter_need_context
    )(func)
# pylint: enable=unexpected-keyword-arg, no-value-for-parameter
