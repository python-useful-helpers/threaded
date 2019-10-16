#    Copyright 2017 - 2019 Alexey Stepanov aka penguinolog
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

# Local Implementation
from ._asynciotask import AsyncIOTask
from ._asynciotask import asynciotask
from ._threaded import Threaded
from ._threaded import threaded
from ._threadpooled import ThreadPooled
from ._threadpooled import threadpooled

cpdef tuple __all__ = (
    "ThreadPooled",
    "Threaded",
    "threadpooled",
    "threaded",
    "AsyncIOTask",
    "asynciotask",
)

cpdef str __version__

try:
    from ._version import version as __version__
except ImportError:
    pass

cpdef str __author__ = "Alexey Stepanov"
cpdef str __author_email__ = "penguinolog@gmail.com"
cpdef dict __maintainers__ = {
    "Alexey Stepanov": "penguinolog@gmail.com",
    "Antonio Esposito": "esposito.cloud@gmail.com",
    "Dennis Dmitriev": "dis-xcom@gmail.com",
}
cpdef str __url__ = "https://github.com/python-useful-helpers/threaded"
cpdef str __description__ = "Decorators for running functions in Thread/ThreadPool/IOLoop"
cpdef str __license__ = "Apache License, Version 2.0"
