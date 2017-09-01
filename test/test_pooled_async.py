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

try:
    import asyncio
except ImportError:
    asyncio = None
import concurrent.futures
import threading
import unittest

import threaded


@unittest.skipIf(asyncio is None, 'No asyncio')
class TestThreadPooled(unittest.TestCase):
    def tearDown(self):
        threaded.ThreadPooled.shutdown()

    def test_thread_pooled_default(self):
        @threaded.threadpooled
        @asyncio.coroutine
        def test():
            return threading.current_thread().name

        pooled_name = concurrent.futures.wait([test()])
        self.assertNotEqual(pooled_name, threading.current_thread().name)

    def test_thread_pooled_construct(self):
        @threaded.threadpooled()
        @asyncio.coroutine
        def test():
            return threading.current_thread().name

        pooled_name = concurrent.futures.wait([test()])
        self.assertNotEqual(pooled_name, threading.current_thread().name)

    def test_thread_pooled_loop(self):
        loop = asyncio.get_event_loop()

        @threaded.threadpooled(loop_getter=loop)
        @asyncio.coroutine
        def test():
            return threading.current_thread().name

        pooled_name = loop.run_until_complete(asyncio.wait_for(test(), 1))
        self.assertNotEqual(pooled_name, threading.current_thread().name)

    def test_thread_pooled_loop_getter(self):
        loop = asyncio.get_event_loop()

        @threaded.threadpooled(loop_getter=asyncio.get_event_loop)
        @asyncio.coroutine
        def test():
            return threading.current_thread().name

        pooled_name = loop.run_until_complete(asyncio.wait_for(test(), 1))
        self.assertNotEqual(pooled_name, threading.current_thread().name)

    def test_thread_pooled_loop_getter_context(self):
        loop = asyncio.get_event_loop()

        def loop_getter(target):
            return target

        @threaded.threadpooled(
            loop_getter=loop_getter,
            loop_getter_need_context=True
        )
        @asyncio.coroutine
        def test(*args, **kwargs):
            return threading.current_thread().name

        pooled_name = loop.run_until_complete(
            asyncio.wait_for(test(loop), 1)
        )
        self.assertNotEqual(pooled_name, threading.current_thread().name)


@unittest.skipIf(asyncio is None, 'No asyncio')
class TestAsyncIOTask(unittest.TestCase):
    def test_default(self):
        @threaded.asynciotask
        @asyncio.coroutine
        def test():
            return 'test'

        loop = asyncio.get_event_loop()
        res = loop.run_until_complete(asyncio.wait_for(test(), 1))
        self.assertEqual(res, 'test')

    def test_construct(self):
        @threaded.asynciotask()
        @asyncio.coroutine
        def test():
            return 'test'

        loop = asyncio.get_event_loop()
        res = loop.run_until_complete(asyncio.wait_for(test(), 1))
        self.assertEqual(res, 'test')
