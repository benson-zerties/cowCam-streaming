#!/usr/bin/python3
# -*- coding: utf-8 -*-

import sys

import unittest
from unittest.mock import patch, Mock
import time
from timeit import default_timer as timer

sys.path.append('..')
from resettable_timer import ResettableTimer

class ResettableTimerTest(unittest.TestCase):
    def setUp(self):
        pass

    def test_timer_expires(self):
        TIMER_CNT_DOWN = 0.5
        end_time  = 0
        def timer_callback():
            nonlocal end_time
            end_time = timer()

        my_timer = ResettableTimer(TIMER_CNT_DOWN, timer_callback)
        start_time = timer()
        my_timer.start()
        time.sleep(0.5)
        self.assertAlmostEqual(end_time - start_time, TIMER_CNT_DOWN, places=2)

    def test_timer_expires_with_args(self):
        TIMER_CNT_DOWN = 0.5
        end_time  = 0
        timer_arg = 'hallo'
        arg_from_cb = None

        def timer_callback(arg):
            nonlocal end_time
            nonlocal arg_from_cb
            end_time = timer()
            arg_from_cb = arg

        my_timer = ResettableTimer(TIMER_CNT_DOWN, timer_callback, timer_arg)
        start_time = timer()
        my_timer.start()
        time.sleep(0.5)
        self.assertAlmostEqual(end_time - start_time, TIMER_CNT_DOWN, places=2)
        assert arg_from_cb == timer_arg


    def test_timer_cancelled(self):
        end_time  = 0
        def timer_callback():
            nonlocal end_time
            end_time = timer()

        my_timer = ResettableTimer(1, timer_callback)
        start_time = timer()
        my_timer.start()
        time.sleep(0.5)
        my_timer.stop()
        assert end_time == 0

if __name__ == '__main__':
    unittest.main()
