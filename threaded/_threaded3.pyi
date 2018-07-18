import asyncio
import concurrent.futures
import threading
import typing
from . import _base_threaded, _class_decorator

class ThreadPooled(_base_threaded.BasePooled):
    def __init__(
        self,
        func: typing.Optional[typing.Callable]=...,
        *,
        loop_getter: typing.Optional[typing.Union[typing.Callable[..., asyncio.AbstractEventLoop], asyncio.AbstractEventLoop]]=...,
        loop_getter_need_context: bool=...
    ) -> None: ...

    @property
    def loop_getter(self) -> typing.Optional[typing.Union[typing.Callable[..., asyncio.AbstractEventLoop], asyncio.AbstractEventLoop]]: ...

    @property
    def loop_getter_need_context(self) -> bool: ...

    def _get_function_wrapper(self, func: typing.Callable) -> typing.Callable[..., typing.Union[concurrent.futures.Future, asyncio.Task]]: ...  # type: ignore

class Threaded(_base_threaded.BaseThreaded):
    def _get_function_wrapper(self, func: typing.Callable) -> typing.Callable[..., threading.Thread]: ...

class AsyncIOTask(_class_decorator.BaseDecorator):
    def __init__(
        self,
        func: typing.Optional[typing.Callable]=...,
        *,
        loop_getter: typing.Union[typing.Callable[..., asyncio.AbstractEventLoop], asyncio.AbstractEventLoop]=...,
        loop_getter_need_context: bool=...
    ) -> None: ...

    @property
    def loop_getter(self) -> typing.Union[typing.Callable[..., asyncio.AbstractEventLoop], asyncio.AbstractEventLoop]: ...

    @property
    def loop_getter_need_context(self) -> bool: ...

    def _get_function_wrapper(self, func: typing.Callable) -> typing.Callable[..., asyncio.Task]: ...


@typing.overload
def threadpooled(
    func: typing.Callable,
    *,
    loop_getter: None = ...,
    loop_getter_need_context: bool = ...

) -> typing.Callable[..., concurrent.futures.Future]: ...

@typing.overload
def threadpooled(
    func: typing.Callable,
    *,
    loop_getter: typing.Union[
        typing.Callable[..., asyncio.AbstractEventLoop],
        asyncio.AbstractEventLoop
    ],
    loop_getter_need_context: bool = ...

) -> typing.Callable[..., asyncio.Task]: ...

@typing.overload
def threadpooled(
    func: None = ...,
    *,
    loop_getter: typing.Union[
        None,
        typing.Callable[..., asyncio.AbstractEventLoop],
        asyncio.AbstractEventLoop
    ]=...,
    loop_getter_need_context: bool = ...
) -> ThreadPooled: ...


@typing.overload
def threaded(name: typing.Callable, daemon: bool = ..., started: bool = ...) -> typing.Callable[..., threading.Thread]: ...

@typing.overload
def threaded(name: typing.Optional[str] = ..., daemon: bool = ..., started: bool = ...) -> Threaded: ...


@typing.overload
def asynciotask(
    func: None= ...,
    *,
    loop_getter: typing.Union[
        typing.Callable[..., asyncio.AbstractEventLoop],
        asyncio.AbstractEventLoop
    ]=asyncio.get_event_loop,
    loop_getter_need_context: bool = ...
) -> AsyncIOTask: ...

@typing.overload
def asynciotask(
    func: typing.Callable,
    *,
    loop_getter: typing.Union[
        typing.Callable[..., asyncio.AbstractEventLoop],
        asyncio.AbstractEventLoop
    ]=asyncio.get_event_loop,
    loop_getter_need_context: bool = ...
) -> typing.Callable[..., asyncio.Task]: ...
