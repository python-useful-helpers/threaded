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

"""threaded module."""

from __future__ import absolute_import

import sys

PY3 = sys.version_info[:2] > (3, 0)

# pylint: disable=no-name-in-module
if PY3:  # pragma: no cover
    from ._threaded3 import (
        ThreadPooled,
        Threaded,
        AsyncIOTask,
        threadpooled,
        threaded,
        asynciotask
    )

    try:  # pragma: no cover
        from ._gthreadpooled3 import GThreadPooled, gthreadpooled
    except ImportError:  # pragma: no cover
        GThreadPooled = gthreadpooled = None
else:  # pragma: no cover
    from ._threaded2 import (
        ThreadPooled,
        Threaded,
        threadpooled,
        threaded,
    )
    try:  # pragma: no cover
        from ._gthreadpooled2 import GThreadPooled, gthreadpooled
    except ImportError:  # pragma: no cover
        GThreadPooled = gthreadpooled = None
# pylint: enable=no-name-in-module


__all__ = (
    'ThreadPooled', 'Threaded',
    'threadpooled', 'threaded'
)

if PY3:  # pragma: no cover
    __all__ += (
        'AsyncIOTask',
        'asynciotask'
    )
if GThreadPooled is not None:  # pragma: no cover
    __all__ += (
        'GThreadPooled',
        'gthreadpooled'
    )

__version__ = '0.9.0'
__author__ = "Alexey Stepanov"
__author_email__ = 'penguinolog@gmail.com'
__url__ = 'https://github.com/penguinolog/threaded'
__description__ = (
    "Decorators for running functions in Thread/ThreadPool/IOLoop"
)
__license__ = "Apache License, Version 2.0"
