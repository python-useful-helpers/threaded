import concurrent.futures
import typing
from . import _class_decorator
from multiprocessing import cpu_count as cpu_count

class APIPooled(_class_decorator.BaseDecorator):
    @classmethod
    def configure(cls, max_workers: typing.Optional[int]=...) -> None: ...

    @classmethod
    def shutdown(cls) -> None: ...

    @property
    def executor(self) -> typing.Any: ...

class BasePooled(APIPooled):
    @classmethod
    def configure(cls, max_workers: int=...) -> None: ...

    @classmethod
    def shutdown(cls) -> None: ...

    @property
    def executor(self) -> ThreadPoolExecutor: ...

class BaseThreaded(_class_decorator.BaseDecorator):
    def __init__(
        self,
        name: typing.Optional[typing.Union[str, typing.Callable]]=...,
        daemon: bool=...,
        started: bool=...
    ) -> None: ...

    @property
    def name(self) -> typing.Optional[str]: ...

    @property
    def daemon(self) -> bool: ...

    @property
    def started(self) -> bool: ...

class ThreadPoolExecutor(concurrent.futures.ThreadPoolExecutor):
    def __init__(self, max_workers: typing.Optional[int]=...) -> None: ...

    @property
    def max_workers(self) -> int: ...

    @property
    def is_shutdown(self) -> bool: ...
