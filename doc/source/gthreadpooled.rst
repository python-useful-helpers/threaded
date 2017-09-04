.. GThreadPooled, gthreadpooled.

API: Decorators: `GThreadPooled`, `gthreadpooled`.
==================================================

.. py:module:: pooled
.. py:currentmodule:: pooled

.. py:class:: GThreadPooled(func, )

    Post function to gevent.threadpool.ThreadPool.

    :param func: function to wrap
    :type func: typing.Optional[typing.Callable[..., typing.Union[typing.Any, typing.Awaitable]]]

    .. note:: Attributes is read-only

    .. py:attribute:: executor

        ``gevent.threadpool.ThreadPool`` instance. Class-wide.

    .. py:attribute:: _func

        ``typing.Optional[typing.Callable[..., typing.Union[typing.Any, typing.Awaitable]]]``
        Wrapped function. Used for inheritance only.

    .. py:classmethod:: configure(max_workers=None, hub=None)

        Pool executor create and configure.

        :param max_workers: Maximum workers
        :type max_workers: typing.Optional[int]
        :param hub: Event-loop hub
        :type hub: typing.Optional[gevent.hub.Hub]

        .. note:: max_workers=None means `(CPU_COUNT or 1) * 5`, it's default value.

    .. py:classmethod:: shutdown

        Shutdown executor.

    .. py:method:: __call__(*args, **kwargs)

        Decorator entry point.

        :rtype: typing.Union[typing.Callable[..., gevent.event.AsyncResult], gevent.event.AsyncResult]


.. py:function:: gthreadpooled(func, )

    Post function to gevent.threadpool.ThreadPool.

    :param func: function to wrap
    :type func: typing.Optional[typing.Callable]
    :rtype: GThreadPooled
