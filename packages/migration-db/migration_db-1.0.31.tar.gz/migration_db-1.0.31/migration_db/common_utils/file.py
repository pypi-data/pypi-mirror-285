# !/usr/bin/python3
# -*- coding:utf-8 -*-
"""
@Author: xiaodong.li
@Time: 5/22/2023 3:51 PM
@Description: Description
@File: file.py
"""
import hashlib
import os


def calc_folder_size(dir_path):
    size = 0
    items = os.listdir(dir_path)
    for item in items:
        path_new = os.path.join(dir_path, item)
        if os.path.isfile(path_new):
            size += os.path.getsize(path_new)
        elif os.path.isdir(path_new):
            size += calc_folder_size(path_new)
    return size


def hash_file(file_path):
    with open(file_path, 'rb') as fp:
        m = hashlib.md5()
        while True:
            data = fp.read(50 * 1024 * 1024)
            if not data:
                break
            m.update(data)
    return m.hexdigest()


def hash_folder(file_path):
    m = hashlib.md5()
    for root, dirs, files in os.walk(file_path):
        for file in files:
            with open(os.path.join(root, file), 'rb') as f:
                while True:
                    data = f.read(1024)
                    if not data:
                        break
                    m.update(data)
    return m.hexdigest()
