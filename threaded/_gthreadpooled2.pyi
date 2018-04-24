import gevent.event
import typing
from . import _base_gthreadpooled

class GThreadPooled(_base_gthreadpooled.BaseGThreadPooled): ...

def gthreadpooled(func: typing.Optional[typing.Callable]=...) -> typing.Union[GThreadPooled, gevent.event.AsyncResult]: ...
