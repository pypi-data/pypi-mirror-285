# !/usr/bin/python3
# -*- coding:utf-8 -*-
"""
@Author: xiaodong.li
@Time: 12/23/2020 1:08 PM
@Description: Description
@File: to_json_file.py
"""

import datetime
import json
import os


class ComplexEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, datetime.datetime):
            return obj.strftime('%Y-%m-%d %H:%M:%S')
        if isinstance(obj, datetime.date):
            return obj.strftime('%Y-%m-%d')
        if isinstance(obj, bytes):
            # return str(obj, encoding='utf-8')
            return bytes.decode(obj)
        return json.JSONEncoder.default(self, obj)


def to_json_file(base_path, file_name, obj, sort_keys=True, indent=4):
    if not obj:
        return
    os.makedirs(base_path, exist_ok=True)
    path = f"{base_path}/{file_name}.json"
    with open(path, "w") as fp:
        json.dump(obj, fp, indent=indent, sort_keys=sort_keys, cls=ComplexEncoder)
