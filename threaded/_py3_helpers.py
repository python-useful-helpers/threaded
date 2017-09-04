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

"""Python 3 related helpers."""

# noinspection PyCompatibility
import asyncio
import functools
import typing

__all__ = (
    'get_loop', 'await_if_required'
)


def get_loop(
        self,
        *args, **kwargs
) -> typing.Optional[asyncio.AbstractEventLoop]:
    """Get event loop in decorator class."""
    if callable(self.loop_getter):
        if self.loop_getter_need_context:
            return self.loop_getter(*args, **kwargs)
        return self.loop_getter()
    return self.loop_getter


def await_if_required(target: typing.Callable) -> typing.Callable:
    """Await result if coroutine was returned."""
    @functools.wraps(target)
    def wrapper(*args, **kwargs):
        """Decorator/wrapper."""
        result = target(*args, **kwargs)
        if asyncio.iscoroutine(result):
            loop = asyncio.new_event_loop()
            result = loop.run_until_complete(result)
            loop.close()
        return result
    return wrapper
