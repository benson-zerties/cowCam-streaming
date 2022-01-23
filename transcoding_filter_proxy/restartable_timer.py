#!/usr/bin/python3
# -*- coding: utf-8 -*-

import threading
import logging
import time

class RestartableTimer(threading.Thread):
    def __init__(self, timeout, callback, *args, **kwargs):
        threading.Thread.__init__(self)
        self._stop_event = threading.Event()
        self._timeout = timeout

        self._expirationTimeLock = threading.Lock()
        self._expirationTime = 0;

        #self._lastUpdateTime = time.time()
        self._cb = callback
        self._cb_args = args
        self._cb_kwargs = kwargs

        self.restart()

    def run(self):
        timeout = self._timeout
        while not (self._stop_event.wait(timeout=timeout)):
            with self._expirationTimeLock:
                expirationTime = self._expirationTime
            timeout = expirationTime - time.time()
            if timeout <= 0:
                print('timer expired')
                self._cb(*self._cb_args, **self._cb_kwargs)
                return

    def restart(self):
        with self._expirationTimeLock:
            self._expirationTime = time.time() + self._timeout

    def stop(self):
        self._stop_event.set()

def my_cb(t):
    t_end = time.time()
    print("Ran for ")
    print(t_end - t)

if __name__ == '__main__':
    # testcase 1
    timeout = 5;
    t = RestartableTimer(timeout, my_cb, time.time())
    t.start()
    t.join()

    # testcase 2
    timeout = 5;
    t = RestartableTimer(timeout, my_cb, time.time())
    t_start = time.time()
    print(t_start)
    t.start()
    time.sleep(2)
    t.restart()
    time.sleep(2)
    t.restart()
