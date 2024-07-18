# !/usr/bin/python3
# -*- coding:utf-8 -*-
"""
@Author: xiaodong.li
@Time: 8/16/2022 12:40 PM
@Description: Description
@File: handle_table_action.py
"""
import re

from ..lib.constant import TableActionEnum, NEWLINE_PLACEHOLDER_PATTERN


def set_field_value_to_null(details, all_table, all_table_field) -> list:
    result = list()
    table_fields = re.split(NEWLINE_PLACEHOLDER_PATTERN, details) or list()
    for table_field in table_fields:
        table, field = table_field.split(".")
        if table not in all_table or field not in all_table_field.get(table):
            continue
        sql = f"UPDATE {table} SET {field}=NULL;"
        result.append(sql)
    return result


def delete_all_data_in_the_table(details, all_table):
    result = list()
    tables = re.split(NEWLINE_PLACEHOLDER_PATTERN, details) or list()
    for table in tables:
        if table not in all_table:
            continue
        sql = f"TRUNCATE TABLE {table};"
        result.append(sql)
    return result


def handle_actions(items, all_table, all_table_field):
    result = list()
    for item in items or list():
        action_sql = list()
        action_id = item.get("action_id")
        details = item.get("details")
        if not (action_id and details):
            continue
        if action_id == TableActionEnum.SET_FIELD_VALUE_TO_NULL.id:
            action_sql = set_field_value_to_null(details, all_table, all_table_field)
        elif action_id == TableActionEnum.DELETE_ALL_DATA_IN_THE_TABLE.id:
            action_sql = delete_all_data_in_the_table(details, all_table)
        if action_sql:
            result.extend(action_sql)
    return result
