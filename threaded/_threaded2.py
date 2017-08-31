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
    'Threaded'
)


class ThreadPooled(_base_threaded.BasePooled):
    """ThreadPoolExecutor wrapped."""

    __slots__ = ()


class Threaded(_base_threaded.BaseThreaded):
    """Threaded decorator."""

    __slots__ = ()
