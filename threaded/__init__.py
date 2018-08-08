#    Copyright 2017-2018 Alexey Stepanov aka penguinolog
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

import typing  # noqa  # pylint: disable=unused-import

# pylint: disable=no-name-in-module
from ._threaded import (
    ThreadPooled,
    Threaded,
    AsyncIOTask,
    threadpooled,
    threaded,
    asynciotask
)

try:  # pragma: no cover
    from ._gthreadpooled import GThreadPooled, gthreadpooled
except ImportError:  # pragma: no cover
    GThreadPooled = gthreadpooled = None  # type: ignore
# pylint: enable=no-name-in-module


__all__ = (
    'ThreadPooled', 'Threaded',
    'threadpooled', 'threaded',
    'AsyncIOTask', 'asynciotask'
)  # type: typing.Tuple[str, ...]

if GThreadPooled is not None:  # pragma: no cover
    __all__ += (
        'GThreadPooled',
        'gthreadpooled'
    )

__version__ = '2.0.0'
__author__ = "Alexey Stepanov"
__author_email__ = 'penguinolog@gmail.com'
__maintainers__ = {
    'Alexey Stepanov': 'penguinolog@gmail.com',
    'Antonio Esposito': 'esposito.cloud@gmail.com',
    'Dennis Dmitriev': 'dis-xcom@gmail.com',
}
__url__ = 'https://github.com/python-useful-helpers/threaded'
__description__ = "Decorators for running functions in Thread/ThreadPool/IOLoop"
__license__ = "Apache License, Version 2.0"
