# !/usr/bin/python3
# -*- coding:utf-8 -*-
"""
@Author: xiaodong.li
@Time: 3/12/2021 4:03 PM
@Description: Description
@File: calc_time.py
"""

import time
from functools import wraps

from .log import Logger


def calc_func_time(function):
    @wraps(function)
    def func_time(*args, **kwargs):
        t0 = time.perf_counter()
        result = function(*args, **kwargs)
        t1 = time.perf_counter()
        Logger().info("{0} running time:{1:.8f}s".format(function.__name__, (t1 - t0)))
        return result

    return func_time
