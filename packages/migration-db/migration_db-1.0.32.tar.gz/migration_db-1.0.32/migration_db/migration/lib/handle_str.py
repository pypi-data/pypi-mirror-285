# !/usr/bin/python3
# -*- coding:utf-8 -*-
"""
@Author: xiaodong.li
@Time: 6/24/2022 4:55 PM
@Description: Description
@File: handle_str.py
"""


def split_db_name(data_base):
    temp = data_base.split("_")
    return temp[1], temp[2], int(temp[-1])


def escape_symbol(string):
    if type(string) is str:
        for i in ["'", "\"", "\\"]:
            string = string.replace(i, "\\" + i)
    return string


def sql_escape_symbol(string):
    if type(string) is str:
        for i in ["\\", "'", "\""]:
            string = string.replace(i, "\\" + i)
    return string
