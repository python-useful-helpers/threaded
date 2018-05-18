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

def threadpooled(
    func: typing.Optional[typing.Callable]=...,
    *,
    loop_getter: typing.Union[None, typing.Callable[..., asyncio.AbstractEventLoop], asyncio.AbstractEventLoop]=...,
    loop_getter_need_context: bool=...
) -> typing.Union[ThreadPooled, typing.Callable[..., typing.Union[concurrent.futures.Future, asyncio.Task]]]: ...

def threaded(
    name: typing.Optional[typing.Union[str, typing.Callable]]=...,
    daemon: bool=...,
    started: bool=...
) -> typing.Union[Threaded, typing.Callable[..., threading.Thread]]: ...

def asynciotask(
    func: typing.Optional[typing.Callable]=...,
    *,
    loop_getter: typing.Union[typing.Callable[..., asyncio.AbstractEventLoop], asyncio.AbstractEventLoop]=...,
    loop_getter_need_context: bool=...
) -> typing.Union[AsyncIOTask, typing.Callable[..., asyncio.Task]]: ...
