# !/usr/bin/python3
# -*- coding:utf-8 -*-
"""
@Author: xiaodong.li
@Time: 3/24/2023 9:06 PM
@Description: Description
@File: handle_procedures.py
"""
import re

from ..lib.constant import NEWLINE_PLACEHOLDER_PATTERN

REPLACE_STR_TEMPLATE = 'CALL REPLACE_STR("{table_name}", "{field_name}", "{pre_value}", "{cur_value}", "{separator}", {pos});'


def handle_procedures(fields, values, all_table, all_table_field):
    result = list()
    for new_value, replace_value in values.items():
        t = re.split(NEWLINE_PLACEHOLDER_PATTERN, fields)
        for i in t:
            if not i or 'REPLACE_STR' not in i:
                continue
            tmp_fields = re.split(r"REPLACE_STR|,|\(|\)| ", i)
            while "" in tmp_fields:
                tmp_fields.remove("")
            field = tmp_fields[0]
            table = field.split(".")[0]
            field = field.split(".")[1]
            if table not in all_table or field not in all_table_field.get(table):
                continue
            separator = tmp_fields[1]
            pos = tmp_fields[2]
            result.append(REPLACE_STR_TEMPLATE.format(table_name=table, field_name=field, pre_value=replace_value,
                                                      cur_value=new_value, separator=separator, pos=pos))
    return result
