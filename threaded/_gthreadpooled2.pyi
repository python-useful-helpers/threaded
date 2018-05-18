import gevent.event  # type: ignore
import typing
from . import _base_gthreadpooled

class GThreadPooled(_base_gthreadpooled.BaseGThreadPooled): ...

def gthreadpooled(func: typing.Optional[typing.Callable]=...) -> typing.Union[GThreadPooled, typing.Callable[..., gevent.event.AsyncResult]]: ...
