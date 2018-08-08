.. ThreadPooled, threadpooled.

API: Decorators: `ThreadPooled`, `threadpooled`.
================================================

.. py:module:: pooled
.. py:currentmodule:: pooled

.. py:class:: ThreadPooled

    Post function to ThreadPoolExecutor.

    .. py:method:: __init__(func, *, loop_getter, loop_getter_need_context, )

        :param func: function to wrap
        :type func: typing.Optional[typing.Callable[..., typing.Union[typing.Any, typing.Awaitable]]]

        :param loop_getter: Method to get event loop, if wrap in asyncio task
        :type loop_getter: typing.Union[None, typing.Callable[..., asyncio.AbstractEventLoop], asyncio.AbstractEventLoop]

        :param loop_getter_need_context: Loop getter requires function context
        :type loop_getter_need_context: bool

    .. note:: Attributes is read-only

    .. py:attribute:: loop_getter

        ``typing.Union[None, typing.Callable[..., asyncio.AbstractEventLoop], asyncio.AbstractEventLoop]``
        Loop getter. If None: use ``concurent.futures.Future``, else use ``EventLoop`` for wrapped function.

    .. py:attribute:: loop_getter_need_context

        ``bool`` - Loop getter will use function call arguments.

    .. py:attribute:: executor

        ``ThreadPoolExecutor`` instance. Class-wide.

        :rtype: ThreadPoolExecutor

    .. py:attribute:: _func

        ``typing.Optional[typing.Callable[..., typing.Union[typing.Any, typing.Awaitable]]]``
        Wrapped function. Used for inheritance only.

    .. py:classmethod:: configure(max_workers=None)

        Pool executor create and configure.

        :param max_workers: Maximum workers
        :type max_workers: typing.Optional[int]

        .. note:: max_workers=None means `CPU_COUNT * 5`, it's default value.

    .. py:classmethod:: shutdown

        Shutdown executor.

    .. py:method:: __call__(*args, **kwargs)

        Decorator entry point.

        :rtype: typing.Union[concurrent.futures.Future, typing.Awaitable, typing.Callable[..., typing.Union[typing.Awaitable, concurrent.futures.Future]]]


.. py:function:: threadpooled(func, *, loop_getter, loop_getter_need_context, )

    Post function to ThreadPoolExecutor.

    :param func: function to wrap
    :type func: typing.Optional[typing.Callable[..., typing.Union[typing.Any, typing.Awaitable]]]

    :param loop_getter: Method to get event loop, if wrap in asyncio task
    :type loop_getter: typing.Union[None, typing.Callable[..., asyncio.AbstractEventLoop], asyncio.AbstractEventLoop]
    :param loop_getter_need_context: Loop getter requires function context
    :type loop_getter_need_context: bool
    :rtype: typing.Union[ThreadPooled, typing.Callable[..., typing.Union[concurrent.futures.Future, typing.Awaitable]]]

Not exported, but public accessed data type:

.. py:class:: ThreadPoolExecutor(max_workers=None)

    Provide readers for protected attributes.

    Simply extend concurrent.futures.ThreadPoolExecutor.

    :param max_workers: Maximum workers allowed. If none: cpu_count() * 5
    :type max_workers: typing.Optional[int]

    .. py:attribute:: max_workers

        ``int`` - max workers variable.

    .. py:attribute:: is_shutdown

        ``bool`` - executor in shutdown state.
