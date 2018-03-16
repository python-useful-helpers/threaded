#    Copyright 2017 Alexey Stepanov aka penguinolog
##
#    Licensed under the Apache License, Version 2.0 (the "License"); you may
#    not use this file except in compliance with the License. You may obtain
#    a copy of the License at
#
#         http://www.apache.org/licenses/LICENSE-2.0
#
#    Unless required by applicable law or agreed to in writing, software
#    distributed under the License is distributed on an "AS IS" BASIS, WITHOUT
#    WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the
#    License for the specific language governing permissions and limitations
#    under the License.

"""Python 2 threaded implementation.

Uses backport of concurrent.futures.
"""

from __future__ import absolute_import

from . import _base_threaded

__all__ = (
    'ThreadPooled',
    'Threaded',
    'threadpooled',
    'threaded',
)


class ThreadPooled(_base_threaded.BasePooled):
    """Post function to ThreadPoolExecutor."""

    __slots__ = ()


class Threaded(_base_threaded.BaseThreaded):
    """Run function in separate thread."""

    __slots__ = ()


# pylint: disable=unexpected-keyword-arg, no-value-for-parameter
def threadpooled(func=None):
    """Post function to ThreadPoolExecutor.

    :param func: function to wrap
    :type func: typing.Optional[typing.Callable]
    :rtype: ThreadPooled
    """
    if func is None:
        return ThreadPooled(func=func)
    return ThreadPooled(func=None)(func)


def threaded(
    name=None,
    daemon=False,
    started=False
):
    """Run function in separate thread.

    :param name: New thread name.
                 If callable: use as wrapped function.
                 If none: use wrapped function name.
    :type name: typing.Union[None, str, typing.Callable]
    :param daemon: Daemonize thread.
    :type daemon: bool
    :param started: Return started thread
    :type started: bool
    :rtype: Threaded
    """
    if callable(name):
        func, name = (
            name,
            'Threaded: ' + getattr(name, '__name__', str(hash(name)))
        )
        return Threaded(name=name, daemon=daemon, started=started)(func)
    return Threaded(name=name, daemon=daemon, started=started)
# pylint: enable=unexpected-keyword-arg, no-value-for-parameter
