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

"""Python 3 threaded implementation.

Asyncio is supported
"""

import asyncio
import concurrent.futures
import functools
import threading
import typing

from . import _base_threaded
from . import _class_decorator

__all__ = (
    'ThreadPooled',
    'Threaded',
    'AsyncIOTask',
    'threadpooled',
    'threaded',
    'asynciotask',
)


def _await_if_required(target: typing.Callable) -> typing.Callable[..., typing.Any]:
    """Await result if coroutine was returned."""
    @functools.wraps(target)
    def wrapper(
        *args: typing.Tuple,
        **kwargs: typing.Dict
    ) -> typing.Any:
        """Decorator/wrapper."""
        result = target(*args, **kwargs)
        if asyncio.iscoroutine(result):
            loop = asyncio.new_event_loop()
            result = loop.run_until_complete(result)
            loop.close()
        return result

    return wrapper


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
        loop_getter: typing.Optional[
            typing.Union[
                typing.Callable[..., asyncio.AbstractEventLoop],
                asyncio.AbstractEventLoop
            ]
        ] = None,
        loop_getter_need_context: bool = False
    ) -> None:
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
    ) -> typing.Optional[
        typing.Union[
            typing.Callable[..., asyncio.AbstractEventLoop],
            asyncio.AbstractEventLoop
        ]
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

    def _get_loop(
        self,
        *args: typing.Tuple,
        **kwargs: typing.Dict
    ) -> typing.Optional[asyncio.AbstractEventLoop]:
        """Get event loop in decorator class."""
        if callable(self.loop_getter):
            if self.loop_getter_need_context:
                return self.loop_getter(*args, **kwargs)  # pylint: disable=not-callable
            return self.loop_getter()  # pylint: disable=not-callable
        return self.loop_getter

    def _get_function_wrapper(
        self,
        func: typing.Callable
    ) -> typing.Callable[..., typing.Union[typing.Awaitable, concurrent.futures.Future]]:
        """Here should be constructed and returned real decorator.

        :param func: Wrapped function
        :type func: typing.Callable
        :return: wrapped coroutine or function
        :rtype: typing.Callable[..., typing.Union[typing.Awaitable, concurrent.futures.Future]]
        """
        prepared = _await_if_required(func)

        # pylint: disable=missing-docstring
        # noinspection PyMissingOrEmptyDocstring
        @functools.wraps(prepared)
        def wrapper(
            *args: typing.Tuple,
            **kwargs: typing.Dict
        ) -> typing.Union[
            typing.Awaitable, concurrent.futures.Future,
            typing.Callable[..., typing.Union[typing.Awaitable, concurrent.futures.Future]]
        ]:
            loop = self._get_loop(*args, **kwargs)  # type: ignore

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

    def __call__(  # pylint: disable=useless-super-delegation
        self,
        *args: typing.Union[typing.Tuple, typing.Callable],
        **kwargs: typing.Dict
    ) -> typing.Union[
        concurrent.futures.Future, typing.Awaitable,
        typing.Callable[..., typing.Union[typing.Awaitable, concurrent.futures.Future]]
    ]:
        """Callable instance."""
        return super(ThreadPooled, self).__call__(*args, **kwargs)  # type: ignore

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


class Threaded(_class_decorator.BaseDecorator):
    """Run function in separate thread."""

    __slots__ = (
        '__name',
        '__daemon',
        '__started',
    )

    def __init__(
        self,
        name: typing.Optional[typing.Union[str, typing.Callable]] = None,
        daemon: bool = False,
        started: bool = False,
    ) -> None:
        """Run function in separate thread.

        :param name: New thread name.
                     If callable: use as wrapped function.
                     If none: use wrapped function name.
        :type name: typing.Optional[typing.Union[str, typing.Callable]]
        :param daemon: Daemonize thread.
        :type daemon: bool
        :param started: Return started thread
        :type started: bool
        """
        # pylint: disable=assigning-non-slot
        self.__daemon = daemon
        self.__started = started
        if callable(name):
            func = name  # type: typing.Callable
            self.__name = 'Threaded: ' + getattr(name, '__name__', str(hash(name)))  # type: str
        else:
            func, self.__name = None, name  # type: ignore
        super(Threaded, self).__init__(func=func)
        # pylint: enable=assigning-non-slot

    @property
    def name(self) -> typing.Optional[str]:
        """Thread name.

        :rtype: typing.Optional[str]
        """
        return self.__name

    @property
    def daemon(self) -> bool:
        """Start thread as daemon.

        :rtype: bool
        """
        return self.__daemon

    @property
    def started(self) -> bool:
        """Return started thread.

        :rtype: bool
        """
        return self.__started

    def __repr__(self) -> str:
        """For debug purposes."""
        return (
            "{cls}("
            "name={self.name!r}, "
            "daemon={self.daemon!r}, "
            "started={self.started!r}, "
            ")".format(
                cls=self.__class__.__name__,
                self=self,
            )
        )  # pragma: no cover

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
        prepared = _await_if_required(func)
        name = self.name
        if name is None:
            name = 'Threaded: ' + getattr(
                func,
                '__name__',
                str(hash(func))
            )

        # pylint: disable=missing-docstring
        # noinspection PyMissingOrEmptyDocstring
        @functools.wraps(prepared)
        def wrapper(
            *args,  # type: typing.Tuple
            **kwargs  # type: typing.Dict
        ) -> threading.Thread:
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

    def __call__(  # pylint: disable=useless-super-delegation
        self,
        *args: typing.Union[typing.Tuple, typing.Callable],
        **kwargs: typing.Dict
    ) -> typing.Union[threading.Thread, typing.Callable[..., threading.Thread]]:
        """Executable instance."""
        return super(Threaded, self).__call__(*args, **kwargs)  # type: ignore


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
        ] = asyncio.get_event_loop,
        loop_getter_need_context: bool = False
    ) -> None:
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

    def get_loop(
        self,
        *args,  # type: typing.Tuple
        **kwargs  # type: typing.Dict
    ) -> asyncio.AbstractEventLoop:
        """Get event loop in decorator class."""
        if callable(self.loop_getter):
            if self.loop_getter_need_context:
                return self.loop_getter(*args, **kwargs)  # pylint: disable=not-callable
            return self.loop_getter()  # pylint: disable=not-callable
        return self.loop_getter

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
        # noinspection PyMissingOrEmptyDocstring
        @functools.wraps(func)
        def wrapper(
            *args,  # type: typing.Tuple
            **kwargs  # type: typing.Dict
        ) -> asyncio.Task:
            loop = self.get_loop(*args, **kwargs)  # type: ignore
            return loop.create_task(func(*args, **kwargs))

        # pylint: enable=missing-docstring
        return wrapper

    def __call__(  # pylint: disable=useless-super-delegation
        self,
        *args: typing.Union[typing.Tuple, typing.Callable],
        **kwargs: typing.Dict
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
            ") at 0x{id:X}>".format(
                cls=self.__class__.__name__,
                func=self._func,
                self=self,
                id=id(self)
            )
        )  # pragma: no cover


# pylint: disable=function-redefined, unused-argument
@typing.overload
def threadpooled(
    func: typing.Callable,
    *,
    loop_getter: None = None,
    loop_getter_need_context: bool = False
) -> typing.Callable[..., concurrent.futures.Future]:
    """Overload: function callable, no loop getter."""
    pass  # pragma: no cover


@typing.overload  # noqa: F811
def threadpooled(
    func: typing.Callable,
    *,
    loop_getter: typing.Union[
        typing.Callable[..., asyncio.AbstractEventLoop],
        asyncio.AbstractEventLoop
    ],
    loop_getter_need_context: bool = False
) -> typing.Callable[..., asyncio.Task]:
    """Overload: function callable, loop getter available."""
    pass  # pragma: no cover


@typing.overload  # noqa: F811
def threadpooled(
    func: None = None,
    *,
    loop_getter: typing.Union[
        None,
        typing.Callable[..., asyncio.AbstractEventLoop],
        asyncio.AbstractEventLoop
    ] = None,
    loop_getter_need_context: bool = False
) -> ThreadPooled:
    """Overload: No function."""
    pass  # pragma: no cover


# pylint: enable=unused-argument
# pylint: disable=unexpected-keyword-arg, no-value-for-parameter
def threadpooled(  # noqa: F811
    func: typing.Optional[typing.Callable] = None,
    *,
    loop_getter: typing.Union[
        None,
        typing.Callable[..., asyncio.AbstractEventLoop],
        asyncio.AbstractEventLoop
    ] = None,
    loop_getter_need_context: bool = False
) -> typing.Union[
    ThreadPooled,
    typing.Callable[..., typing.Union[concurrent.futures.Future, typing.Awaitable]]
]:
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
    :rtype: typing.Union[ThreadPooled, typing.Callable[..., typing.Union[concurrent.futures.Future, typing.Awaitable]]]
    """
    if func is None:
        return ThreadPooled(
            func=func,
            loop_getter=loop_getter,
            loop_getter_need_context=loop_getter_need_context
        )
    return ThreadPooled(  # type: ignore
        func=None,
        loop_getter=loop_getter,
        loop_getter_need_context=loop_getter_need_context
    )(func)


# pylint: disable=unused-argument
@typing.overload
def threaded(
    name: typing.Callable,
    daemon: bool = False,
    started: bool = False
) -> typing.Callable[..., threading.Thread]:
    """Overload: Call decorator without arguments."""
    pass  # pragma: no cover


@typing.overload  # noqa: F811
def threaded(
    name: typing.Optional[str] = None,
    daemon: bool = False,
    started: bool = False
) -> Threaded:
    """Overload: Name is not callable."""
    pass  # pragma: no cover


# pylint: enable=unused-argument
def threaded(  # noqa: F811
    name: typing.Optional[typing.Union[str, typing.Callable]] = None,
    daemon: bool = False,
    started: bool = False
) -> typing.Union[Threaded, typing.Callable[..., threading.Thread]]:
    """Run function in separate thread.

    :param name: New thread name.
                 If callable: use as wrapped function.
                 If none: use wrapped function name.
    :type name: typing.Union[None, str, typing.Callable]
    :param daemon: Daemonize thread.
    :type daemon: bool
    :param started: Return started thread
    :type started: bool
    :rtype: typing.Union[Threaded, typing.Callable[..., threading.Thread]]
    """
    if callable(name):
        func, name = (
            name,
            'Threaded: ' + getattr(name, '__name__', str(hash(name)))
        )
        return Threaded(name=name, daemon=daemon, started=started)(func)  # type: ignore
    return Threaded(name=name, daemon=daemon, started=started)


# pylint: disable=unused-argument
@typing.overload
def asynciotask(
    func: None = None,
    *,
    loop_getter: typing.Union[
        typing.Callable[..., asyncio.AbstractEventLoop],
        asyncio.AbstractEventLoop
    ] = asyncio.get_event_loop,
    loop_getter_need_context: bool = False
) -> AsyncIOTask:
    """Overload: no function."""
    pass  # pragma: no cover


@typing.overload  # noqa: F811
def asynciotask(
    func: typing.Callable,
    *,
    loop_getter: typing.Union[
        typing.Callable[..., asyncio.AbstractEventLoop],
        asyncio.AbstractEventLoop
    ] = asyncio.get_event_loop,
    loop_getter_need_context: bool = False
) -> typing.Callable[..., asyncio.Task]:
    """Overload: provided function."""
    pass  # pragma: no cover


# pylint: enable=unused-argument
def asynciotask(  # noqa: F811
    func: typing.Optional[typing.Callable] = None,
    *,
    loop_getter: typing.Union[
        typing.Callable[..., asyncio.AbstractEventLoop],
        asyncio.AbstractEventLoop
    ] = asyncio.get_event_loop,
    loop_getter_need_context: bool = False
) -> typing.Union[AsyncIOTask, typing.Callable[..., asyncio.Task]]:
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
    :rtype: typing.Union[AsyncIOTask, typing.Callable[..., asyncio.Task]]
    """
    if func is None:
        return AsyncIOTask(
            func=func,
            loop_getter=loop_getter,
            loop_getter_need_context=loop_getter_need_context
        )
    return AsyncIOTask(  # type: ignore
        func=None,
        loop_getter=loop_getter,
        loop_getter_need_context=loop_getter_need_context
    )(func)
# pylint: enable=unexpected-keyword-arg, no-value-for-parameter, function-redefined
