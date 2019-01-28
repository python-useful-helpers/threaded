.. ThreadPooled, threadpooled.

API: Decorators: `ThreadPooled`, `threadpooled`.
================================================

.. py:module:: pooled
.. py:currentmodule:: pooled

.. py:class:: ThreadPooled(object)

    Post function to ThreadPoolExecutor.

    .. py:method:: __init__(func, *, loop_getter, loop_getter_need_context, )

        :param func: function to wrap
        :type func: typing.Optional[typing.Callable[..., typing.Union[typing.Any, typing.Awaitable]]]

    .. note:: Attributes is read-only

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

        .. note:: max_workers=None means `(CPU_COUNT or 1) * 5`, it's default value.

    .. py:classmethod:: shutdown

        Shutdown executor.

    .. py:method:: __call__(*args, **kwargs)

        Decorator entry point.

        :rtype: typing.Union[typing.Callable[..., typing.Union[concurrent.futures.Future, asyncio.Task]], typing.Union[concurrent.futures.Future, asyncio.Task]]


.. py:function:: threadpooled(func, *, loop_getter, loop_getter_need_context, )

    Post function to ThreadPoolExecutor.

    :param func: function to wrap
    :type func: typing.Optional[typing.Callable[..., typing.Union[typing.Any, typing.Awaitable]]]

    :rtype: typing.Union[ThreadPooled, typing.Callable[..., typing.Union[concurrent.futures.Future, asyncio.Task]]]

Not exported, but public accessed data type:

.. py:class:: ThreadPoolExecutor(max_workers=None)

    Provide readers for protected attributes.

    Simply extend concurrent.futures.ThreadPoolExecutor.

    :param max_workers: Maximum workers allowed. If none: cpu_count() or 1) * 5
    :type max_workers: typing.Optional[int]

    .. py:attribute:: max_workers

        ``int`` - max workers variable.

    .. py:attribute:: is_shutdown

        ``bool`` - executor in shutdown state.
