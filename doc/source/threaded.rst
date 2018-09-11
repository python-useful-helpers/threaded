.. Threaded class and threaded function.

API: Decorators: `Threaded` class and `threaded` function.
==========================================================

.. py:module:: threaded
.. py:currentmodule:: threaded

.. py:class:: Threaded

    Run function in separate thread.

    .. py:method:: __init__(name=None, daemon=False, started=False, )

        :param name: New thread name.
                     If callable: use as wrapped function.
                     If none: use wrapped function name.
        :type name: typing.Optional[typing.Union[str, typing.Callable[..., typing.Union[typing.Any, typing.Awaitable]]]]
        :param daemon: Daemonize thread.
        :type daemon: bool
        :param started: Return started thread
        :type started: bool

    .. note:: Attributes is read-only.

    .. py:attribute:: name

        ``typing.Optional[str]`` - New thread name. If none: use wrapped function name.

    .. py:attribute:: started

        ``bool``

    .. py:attribute:: daemon

        ``bool``

    .. py:attribute:: _func

        Wrapped function. Used for inheritance only.

    .. py:method:: __call__(*args, **kwargs)

        Decorator entry point.

        :rtype: typing.Union[threading.Thread, typing.Callable[..., threading.Thread]]


.. py:function:: threaded(name=None, daemon=False, started=False, )

    Run function in separate thread.

    :param name: New thread name.
                 If callable: use as wrapped function.
                 If none: use wrapped function name.
    :type name: typing.Optional[typing.Union[str, typing.Callable[..., typing.Union[typing.Any, typing.Awaitable]]]]
    :param daemon: Daemonize thread.
    :type daemon: bool
    :param started: Return started thread
    :type started: bool
    :rtype: typing.Union[Threaded, typing.Callable[..., threading.Thread]]
