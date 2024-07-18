# !/usr/bin/python3
# -*- coding:utf-8 -*-
"""
@Author: xiaodong.li
@Time: 5/6/2023 11:13 AM
@Description: Description
@File: handle_external_condition_mapping_data.py
"""
from ..lib.constant import MAPPING_DATA


def handle_external_condition_mapping_data(replace_fields, val):
    for replace_field in replace_fields:
        if MAPPING_DATA in replace_field.external_condition:
            if type(val) is int:
                tmp_mapping_data = "'{0}'".format(MAPPING_DATA)
                tmp_val = str(val)
            else:
                tmp_mapping_data = MAPPING_DATA
                tmp_val = val or str()
            replace_field.external_condition = replace_field.external_condition.replace(tmp_mapping_data, tmp_val)
