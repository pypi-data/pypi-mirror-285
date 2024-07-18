# !/usr/bin/python3
# -*- coding:utf-8 -*-
"""
@Author: xiaodong.li
@Time: 5/28/2024 3:01 PM
@Description: Description
@File: handle_sql_statement.py
"""
import sqlparse
from sqlparse.sql import Identifier


def extract_tables_and_columns(sql):
    parsed = sqlparse.parse(sql)
    table_columns = {}

    for stmt in parsed:
        tokens = stmt.tokens
        for token in tokens:
            table_name = None
            if isinstance(token, Identifier):
                identifier_tokens = token.tokens
                for identifier_token in identifier_tokens:
                    if table_name is None:
                        table_name = identifier_token.value
                    else:
                        raise Exception("error.")
                parsed
    return table_columns


def handle_sql_statement(sql_statement):
    result = list()
    for sql_dto in sql_statement:
        details = sql_dto.get('details')
        result.append(details)
    return result
# # 示例SQL语句
# sql = """
# UPDATE eclinical_entry_form_item_record
# SET current_value=REPLACE(current_value, (SELECT `VALUE` FROM eclinical_system_parameter WHERE `NAME`="CASE_NO_ABBR" AND IS_DELETE=FALSE), ";")
# WHERE item_uuid="1485201938281795585";
# UPDATE eclinical_entry_form_item_record SET delete_version=1 WHERE form_uuid="1506541561834811393";
# """
#
# table_columns = extract_tables_and_columns(sql)
#
# print("Table and Columns Mapping:")
# for table, columns in table_columns.items():
#     print(f"Table: {table}, Columns: {columns}")
