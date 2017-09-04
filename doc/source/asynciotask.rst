.. AsyncIOTask, asynciotask.

API: Decorators: `AsyncIOTask`, `asynciotask`.
================================================

.. py:module:: pooled
.. py:currentmodule:: pooled

.. note:: Python 3 only.

.. py:class:: AsyncIOTask(func, *, loop_getter, loop_getter_need_context, )

    Wrap to asyncio.Task.

    :param func: function to wrap
    :type func: typing.Optional[typing.Callable[..., typing.Awaitable]]
    :param loop_getter: Method to get event loop, if wrap in asyncio task
    :type loop_getter: typing.Union[typing.Callable[..., asyncio.AbstractEventLoop], asyncio.AbstractEventLoop]
    :param loop_getter_need_context: Loop getter requires function context
    :type loop_getter_need_context: bool

    .. note:: Attributes is read-only

    .. py:attribute:: loop_getter

        ``typing.Union[typing.Callable[..., asyncio.AbstractEventLoop], asyncio.AbstractEventLoop]``
        Loop getter.

    .. py:attribute:: loop_getter_need_context

        ``bool`` - Loop getter will use function call arguments.

    .. py:attribute:: _func

        ``typing.Optional[typing.Callable[..., typing.Awaitable]]``
        Wrapped function. Used for inheritance only.

    .. py:method:: __call__(*args, **kwargs)

        Decorator entry point.

        :rtype: typing.Union[typing.Callable[..., asyncio.Task], asyncio.Task]


.. py:function:: asynciotask(func, *, loop_getter, loop_getter_need_context, )

    Wrap to asyncio.Task.

    :param func: function to wrap
    :type func: typing.Optional[typing.Callable[..., typing.Awaitable]]
    :param loop_getter: Method to get event loop, if wrap in asyncio task
    :type loop_getter: typing.Union[typing.Callable[..., asyncio.AbstractEventLoop], asyncio.AbstractEventLoop]
    :param loop_getter_need_context: Loop getter requires function context
    :type loop_getter_need_context: bool
    :rtype: AsyncIOTask
