# !/usr/bin/python3
# -*- coding:utf-8 -*-
"""
@Author: xiaodong.li
@Time: 3/4/2024 5:44 PM
@Description: Description
@File: synchronized.py
"""
import threading


def synchronized(func):
    func.__lock__ = threading.Lock()

    def synced_func(*args, **kwargs):
        with func.__lock__:
            return func(*args, **kwargs)

    return synced_func
