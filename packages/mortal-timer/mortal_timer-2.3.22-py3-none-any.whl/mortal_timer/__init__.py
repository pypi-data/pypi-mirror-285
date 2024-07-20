# cython: language_level=3
# #!/usr/bin/env python
# -*- coding: UTF-8 -*-
"""
@Author: MaJian
@Time: 2024/1/20 17:44
@SoftWare: PyCharm
@Project: mortal
@File: __init__.py
"""
from .timer_main import MortalTimerMain


class MortalTimer(MortalTimerMain):
    def __init__(self, func, *args, **kwargs):
        super().__init__(func, *args, **kwargs)

    def start(self, interval, mark=None, once=False):
        self._start(interval, mark, once)

    def join(self):
        self._join()

    def stop(self):
        self._stop()
