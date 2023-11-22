#    Copyright 2017 - 2020 Alexey Stepanov aka penguinolog
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

"""Threaded implementation.

Asyncio is supported
"""

# Package Implementation
from threaded cimport class_decorator


cdef class Threaded(class_decorator.BaseDecorator):
    """Run function in separate thread."""

    cdef:
        readonly bint daemon
        readonly bint started
        readonly str name
