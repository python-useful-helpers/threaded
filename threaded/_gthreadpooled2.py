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

from . import _base_gthreadpooled

__all__ = (
    'GThreadPooled',
    'gthreadpooled',
)


class GThreadPooled(_base_gthreadpooled.BaseGThreadPooled):
    """Post function to gevent.threadpool.ThreadPool."""

    __slots__ = ()


# pylint: disable=unexpected-keyword-arg, no-value-for-parameter
def gthreadpooled(func=None):
    """Post function to gevent.threadpool.ThreadPool.

    :param func: function to wrap
    :type func: typing.Optional[typing.Callable]
    :rtype: GThreadPooled
    """
    if func is None:
        return GThreadPooled(func=func)
    return GThreadPooled(func=None)(func)
# pylint: enable=unexpected-keyword-arg, no-value-for-parameter
