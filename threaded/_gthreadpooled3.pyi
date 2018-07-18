import gevent.event  # type: ignore
import typing
from . import _base_gthreadpooled

class GThreadPooled(_base_gthreadpooled.BaseGThreadPooled): ...


@typing.overload
def gthreadpooled(func: typing.Callable) -> typing.Callable[..., gevent.event.AsyncResult]: ...

@typing.overload
def gthreadpooled(func: None=...) -> GThreadPooled: ...
