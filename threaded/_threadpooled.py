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

"""ThreadPooled implementation.

Asyncio is supported
"""

__all__ = ("ThreadPooled", "threadpooled")

# Standard Library
import asyncio
import concurrent.futures
import functools
import typing

# Local Implementation
from . import _base_threaded


class ThreadPooled(_base_threaded.APIPooled):
    """Post function to ThreadPoolExecutor."""

    __slots__ = ("__loop_getter", "__loop_getter_need_context")

    __executor: typing.Optional["ThreadPoolExecutor"] = None

    @classmethod
    def configure(cls: typing.Type["ThreadPooled"], max_workers: typing.Optional[int] = None) -> None:
        """Pool executor create and configure.

        :param max_workers: Maximum workers
        :type max_workers: typing.Optional[int]
        """
        if isinstance(cls.__executor, ThreadPoolExecutor):
            if cls.__executor.max_workers == max_workers:
                return
            cls.__executor.shutdown()

        cls.__executor = ThreadPoolExecutor(max_workers=max_workers)

    @classmethod
    def shutdown(cls: typing.Type["ThreadPooled"]) -> None:
        """Shutdown executor."""
        if cls.__executor is not None:
            cls.__executor.shutdown()

    @property
    def executor(self) -> "ThreadPoolExecutor":
        """Executor instance.

        :rtype: ThreadPoolExecutor
        """
        if not isinstance(self.__executor, ThreadPoolExecutor) or self.__executor.is_shutdown:
            self.configure()
        return self.__executor  # type: ignore

    def __init__(
        self,
        func: typing.Optional[typing.Callable[..., typing.Union["typing.Awaitable[typing.Any]", typing.Any]]] = None,
        *,
        loop_getter: typing.Optional[
            typing.Union[typing.Callable[..., asyncio.AbstractEventLoop], asyncio.AbstractEventLoop]
        ] = None,
        loop_getter_need_context: bool = False,
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
        super().__init__(func=func)
        self.__loop_getter: typing.Optional[
            typing.Union[typing.Callable[..., asyncio.AbstractEventLoop], asyncio.AbstractEventLoop]
        ] = loop_getter
        self.__loop_getter_need_context: bool = loop_getter_need_context

    @property
    def loop_getter(
        self,
    ) -> typing.Optional[typing.Union[typing.Callable[..., asyncio.AbstractEventLoop], asyncio.AbstractEventLoop]]:
        """Loop getter.

        :rtype: typing.Union[None, typing.Callable[..., asyncio.AbstractEventLoop], asyncio.AbstractEventLoop]
        """
        return self.__loop_getter

    @property
    def loop_getter_need_context(self) -> bool:
        """Loop getter need execution context.

        :rtype: bool
        """
        return self.__loop_getter_need_context

    def _get_loop(self, *args: typing.Any, **kwargs: typing.Any) -> typing.Optional[asyncio.AbstractEventLoop]:
        """Get event loop in decorator class.

        :return: event loop if available or getter available
        :rtype: Optional[asyncio.AbstractEventLoop]
        """
        if callable(self.loop_getter):
            if self.loop_getter_need_context:
                return self.loop_getter(*args, **kwargs)  # pylint: disable=not-callable
            return self.loop_getter()  # pylint: disable=not-callable
        return self.loop_getter

    def _get_function_wrapper(
        self, func: typing.Callable[..., typing.Union["typing.Awaitable[typing.Any]", typing.Any]]
    ) -> typing.Callable[..., "typing.Union[concurrent.futures.Future[typing.Any], typing.Awaitable[typing.Any]]"]:
        """Here should be constructed and returned real decorator.

        :param func: Wrapped function
        :type func: typing.Callable
        :return: wrapped coroutine or function
        :rtype: Callable[..., Union[Awaitable, concurrent.futures.Future]]
        """
        prepared = self._await_if_required(func)

        # noinspection PyMissingOrEmptyDocstring
        @functools.wraps(prepared)
        def wrapper(
            *args: typing.Any, **kwargs: typing.Any
        ) -> typing.Union["concurrent.futures.Future[typing.Any]", "typing.Awaitable[typing.Any]"]:
            """Main function wrapper.

            :return: coroutine or function
            :rtype: Union[Awaitable, concurrent.futures.Future]
            """
            loop: typing.Optional[asyncio.AbstractEventLoop] = self._get_loop(*args, **kwargs)

            if loop is None:
                return self.executor.submit(prepared, *args, **kwargs)

            return loop.run_in_executor(self.executor, functools.partial(prepared, *args, **kwargs))

        return wrapper

    def __call__(  # pylint: disable=useless-super-delegation
        self,
        *args: typing.Union[typing.Callable[..., typing.Union["typing.Awaitable[typing.Any]", typing.Any]], typing.Any],
        **kwargs: typing.Any,
    ) -> typing.Union[
        "concurrent.futures.Future[typing.Any]",
        "typing.Awaitable[typing.Any]",
        typing.Callable[..., "typing.Union[concurrent.futures.Future[typing.Any], typing.Awaitable[typing.Any]]"],
    ]:
        """Callable instance.

        :return: Future, Awaitable or it's getter (depends of decoration way and asyncio.Loop provided)
        :rtype: Union[concurrent.futures.Future[Any], Awaitable[Any] Callable[..., ...]]
        """
        return super().__call__(*args, **kwargs)  # type: ignore

    def __repr__(self) -> str:  # pragma: no cover
        """For debug purposes.

        :return: repr info
        :rtype: str
        """
        return (
            f"<{self.__class__.__name__}("
            f"{self._func!r}, "
            f"loop_getter={self.loop_getter!r}, "
            f"loop_getter_need_context={self.loop_getter_need_context!r}, "
            f") at 0x{id(self):X}>"
        )


@typing.overload
def threadpooled(
    func: typing.Callable[..., typing.Union["typing.Awaitable[typing.Any]", typing.Any]],
    *,
    loop_getter: None = None,
    loop_getter_need_context: bool = False,
) -> typing.Callable[..., "concurrent.futures.Future[typing.Any]"]:
    """Overload: function callable, no loop getter."""


@typing.overload  # noqa: F811
def threadpooled(
    func: typing.Callable[..., typing.Union["typing.Awaitable[typing.Any]", typing.Any]],
    *,
    loop_getter: typing.Union[typing.Callable[..., asyncio.AbstractEventLoop], asyncio.AbstractEventLoop],
    loop_getter_need_context: bool = False,
) -> typing.Callable[..., "asyncio.Task[typing.Any]"]:
    """Overload: function callable, loop getter available."""


@typing.overload  # noqa: F811
def threadpooled(
    func: None = None,
    *,
    loop_getter: typing.Union[None, typing.Callable[..., asyncio.AbstractEventLoop], asyncio.AbstractEventLoop] = None,
    loop_getter_need_context: bool = False,
) -> ThreadPooled:
    """Overload: No function."""


def threadpooled(  # noqa: F811
    func: typing.Optional[typing.Callable[..., typing.Union["typing.Awaitable[typing.Any]", typing.Any]]] = None,
    *,
    loop_getter: typing.Union[None, typing.Callable[..., asyncio.AbstractEventLoop], asyncio.AbstractEventLoop] = None,
    loop_getter_need_context: bool = False,
) -> typing.Union[
    ThreadPooled,
    typing.Callable[..., "typing.Union[concurrent.futures.Future[typing.Any], typing.Awaitable[typing.Any]]"],
]:
    """Post function to ThreadPoolExecutor.

    :param func: function to wrap
    :type func: typing.Optional[typing.Callable[..., typing.Union[typing.Awaitable, typing.Any]]]
    :param loop_getter: Method to get event loop, if wrap in asyncio task
    :type loop_getter: typing.Union[
                           None,
                           typing.Callable[..., asyncio.AbstractEventLoop],
                           asyncio.AbstractEventLoop
                       ]
    :param loop_getter_need_context: Loop getter requires function context
    :type loop_getter_need_context: bool
    :return: ThreadPooled instance, if called as function or argumented decorator, else callable wrapper
    :rtype: typing.Union[ThreadPooled, typing.Callable[..., typing.Union[concurrent.futures.Future, typing.Awaitable]]]
    """
    if func is None:
        return ThreadPooled(func=func, loop_getter=loop_getter, loop_getter_need_context=loop_getter_need_context)
    return ThreadPooled(  # type: ignore
        func=None, loop_getter=loop_getter, loop_getter_need_context=loop_getter_need_context
    )(func)


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
