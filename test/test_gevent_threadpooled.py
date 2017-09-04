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

from __future__ import absolute_import
from __future__ import unicode_literals

import threading
import unittest

try:
    import gevent
    import gevent.threadpool
except ImportError:
    gevent = None

import six

import threaded

if six.PY3:
    from os import cpu_count
else:
    try:
        from multiprocessing import cpu_count
    except ImportError:
        def cpu_count():
            """Fake CPU count."""
            return 1


@unittest.skipIf(gevent is None, 'No gevent')
class TestThreadPooled(unittest.TestCase):
    def tearDown(self):
        threaded.GThreadPooled.shutdown()

    def test_thread_pooled_default(self):
        @threaded.gthreadpooled
        def test():
            return threading.current_thread().name

        pooled_name = test().wait()
        self.assertNotEqual(pooled_name, threading.current_thread().name)

    def test_thread_pooled_construct(self):
        @threaded.gthreadpooled()
        def test():
            return threading.current_thread().name

        pooled_name = test().wait()
        self.assertNotEqual(pooled_name, threading.current_thread().name)

    def test_thread_pooled_config(self):
        thread_pooled = threaded.gthreadpooled()
        thread_pooled.configure()

        self.assertEqual(
            thread_pooled.executor.maxsize,
            (cpu_count() or 1) * 5
        )

        thread_pooled.configure(max_workers=2)

        @thread_pooled
        def test():
            return threading.current_thread().name

        pooled_name = test().wait()
        self.assertNotEqual(pooled_name, threading.current_thread().name)
        self.assertEqual(thread_pooled.executor.maxsize, 2)

    def test_reconfigure(self):
        """Gevent worker instance is re-used."""
        thread_pooled = threaded.gthreadpooled()
        executor = thread_pooled.executor

        thread_pooled.configure(max_workers=executor.maxsize)
        self.assertIs(executor, thread_pooled.executor)

        old_size = executor.maxsize
        thread_pooled.configure(max_workers=old_size + 1)
        self.assertIs(executor, thread_pooled.executor)
        self.assertEqual(executor.maxsize, old_size + 1)
