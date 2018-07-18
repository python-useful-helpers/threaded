import concurrent.futures
import threading
import typing
from . import _base_threaded

class ThreadPooled(_base_threaded.BasePooled): ...
class Threaded(_base_threaded.BaseThreaded): ...




@typing.overload
def threadpooled(func: typing.Callable) -> typing.Callable[..., concurrent.futures.Future]: ...

@typing.overload
def threadpooled(func: None=...) -> ThreadPooled: ...


@typing.overload
def threaded(name: typing.Callable, daemon: bool=..., started: bool=...) -> typing.Callable[..., threading.Thread]: ...

@typing.overload
def threaded(name: typing.Optional[str]=..., daemon: bool=..., started: bool=...) -> Threaded: ...
