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

"""Python 3 pooled implementation.

Asyncio is supported
"""

# noinspection PyCompatibility
import asyncio
# noinspection PyCompatibility
import concurrent.futures
import functools
import typing


from . import _base_pooled

__all__ = (
    'ThreadPooled',
    'ProcessPooled',
    'AsyncIOTask'
)


# pylint: disable=abstract-method
# noinspection PyAbstractClass
class _Py3Pooled(_base_pooled.BasePooled):
    """Python 3 specific base class."""

    __slots__ = (
        '__loop_getter',
        '__loop_getter_need_context'
    )

    def __init__(
        self,
        *,
        loop_getter: typing.Union[
            None,
            typing.Callable[..., asyncio.AbstractEventLoop],
            asyncio.AbstractEventLoop
        ]=None,
        loop_getter_need_context: bool = False
    ):
        """Wrap function in future and return.

        :param loop_getter: Method to get event loop, if wrap in asyncio task
        :param loop_getter_need_context: Loop getter requires function context
        """
        super(_Py3Pooled, self).__init__()
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
        """Loop getter."""
        return self.__loop_getter

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
        :rtype: typing.Callable
        """
        # pylint: disable=missing-docstring
        # noinspection PyCompatibility,PyMissingOrEmptyDocstring
        def await_if_required(
            target: typing.Callable,
            *args, **kwargs
        ):
            result = target(*args, **kwargs)
            if asyncio.iscoroutine(result):
                inner_loop = asyncio.get_event_loop()
                return inner_loop.run_until_complete(result)
            return result

        prepared = functools.partial(
            await_if_required, func
        )

        # noinspection PyCompatibility,PyMissingOrEmptyDocstring
        @functools.wraps(func)
        def wrapper(
            *args, **kwargs
        ) -> typing.Union[
            concurrent.futures.Future,
            asyncio.Task
        ]:
            if callable(self.__loop_getter):
                if self.__loop_getter_need_context:
                    loop = self.__loop_getter(*args, **kwargs)
                else:
                    loop = self.__loop_getter()
            else:
                loop = self.__loop_getter

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

# pylint: enable=abstract-method


class ThreadPooled(_Py3Pooled):
    """ThreadPoolExecutor wrapped."""

    __slots__ = ()

    __executor = None

    @classmethod
    def configure(
        cls,
        max_workers: typing.Optional[int]=None,
    ):
        """Pool executor create and configure.

        :param max_workers: Maximum workers
        """
        if isinstance(cls.__executor, _base_pooled.ThreadPoolExecutor):
            if cls.__executor.max_workers == max_workers:
                return
            cls.__executor.shutdown()

        cls.__executor = _base_pooled.ThreadPoolExecutor(
            max_workers=max_workers,
        )

    @classmethod
    def shutdown(cls):
        """Shutdown executor."""
        if cls.__executor is not None:
            cls.__executor.shutdown()

    @property
    def executor(self):
        """Executor.

        :rtype: _base_pooled.ThreadPoolExecutor
        """
        if not isinstance(
            self.__executor,
            _base_pooled.ThreadPoolExecutor
        ):
            self.configure()
        return self.__executor


class ProcessPooled(_Py3Pooled):
    """ProcessPoolExecutor wrapped."""

    __slots__ = ()

    __executor = None

    @classmethod
    def configure(
        cls,
        max_workers: typing.Optional[int]=None,
    ):
        """Pool executor create and configure.

        :param max_workers: Maximum workers
        """
        if isinstance(cls.__executor, _base_pooled.ProcessPoolExecutor):
            if cls.__executor.max_workers == max_workers:
                return
            cls.__executor.shutdown()

        cls.__executor = _base_pooled.ProcessPoolExecutor(
            max_workers=max_workers,
        )

    @classmethod
    def shutdown(cls):
        """Shutdown executor."""
        if cls.__executor is not None:
            cls.__executor.shutdown()

    @property
    def executor(self):
        """Executor.

        :rtype: _base_pooled.ProcessPoolExecutor
        """
        if not isinstance(
            self.__executor,
            _base_pooled.ProcessPoolExecutor
        ):
            self.configure()
        return self.__executor


class AsyncIOTask(typing.Callable):
    """Wrap to asyncio.Task."""

    __slots__ = (
        '__loop_getter',
        '__loop_getter_need_context'
    )

    def __init__(
        self,
        *,
        loop_getter: typing.Union[
            typing.Callable[..., asyncio.AbstractEventLoop],
            asyncio.AbstractEventLoop
        ]=asyncio.get_event_loop,
        loop_getter_need_context: bool = False
    ):
        """Wrap function in future and return.

        :param loop_getter: Method to get event loop, if wrap in asyncio task
        :param loop_getter_need_context: Loop getter requires function context
        """
        self.__loop_getter = loop_getter
        self.__loop_getter_need_context = loop_getter_need_context

    @property
    def loop_getter(
            self
    ) -> typing.Union[
        typing.Callable[..., asyncio.AbstractEventLoop],
        asyncio.AbstractEventLoop
    ]:
        """Loop getter."""
        return self.__loop_getter

    def _get_function_wrapper(
        self,
        func: typing.Callable[..., typing.Awaitable]
    ) -> typing.Callable[..., asyncio.Task]:
        """Here should be constructed and returned real decorator.

        :param func: Wrapped function
        """
        # pylint: disable=missing-docstring
        # noinspection PyCompatibility,PyMissingOrEmptyDocstring
        @functools.wraps(func)
        def wrapper(*args, **kwargs) -> asyncio.Task:
            if callable(self.__loop_getter):
                if self.__loop_getter_need_context:
                    loop = self.__loop_getter(*args, **kwargs)
                else:
                    loop = self.__loop_getter()
            else:
                loop = self.__loop_getter

            return loop.create_task(func(*args, **kwargs))

        # pylint: enable=missing-docstring
        return wrapper

    def __call__(
        self,
        func: typing.Callable[..., typing.Awaitable],
        *args, **kwargs
    ) -> typing.Union[asyncio.Task, typing.Callable[..., asyncio.Task]]:
        """Main decorator getter.

        :returns: Decorated function.
        """
        return self._get_function_wrapper(func)
