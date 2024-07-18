# !/usr/bin/python3
# -*- coding:utf-8 -*-
"""
@Author: xiaodong.li
@Time: 6/20/2022 11:36 AM
@Description: Description
@File: table_detail.py
"""


class BuildSqlDto:

    def __init__(self, database=None, replace_fields=None, table_actions=None, procedures=None, sql_statement=None):
        if replace_fields is None:
            replace_fields = list()
        self.database = database
        self.replace_fields = replace_fields
        if table_actions is None:
            table_actions = list()
        self.table_actions = table_actions
        if procedures is None:
            procedures = list()
        self.procedures = procedures
        if sql_statement is None:
            sql_statement = list()
        self.sql_statement = sql_statement


class FieldGroup:
    def __init__(self, new_value=None, replace_value=None, data_type=None, fields=None):
        if fields is None:
            fields = list()
        self.__new_value = new_value
        self.__replace_value = replace_value
        self.__data_type = data_type
        self.__fields = fields

    @property
    def new_value(self):
        return self.__new_value

    @new_value.setter
    def new_value(self, new_value):
        self.__new_value = new_value

    @property
    def replace_value(self):
        return self.__replace_value

    @replace_value.setter
    def replace_value(self, replace_value):
        self.__replace_value = replace_value

    @property
    def data_type(self):
        return self.__data_type

    @data_type.setter
    def data_type(self, data_type):
        self.__data_type = data_type

    @property
    def fields(self):
        return self.__fields

    @fields.setter
    def fields(self, fields):
        self.__fields = fields


class ReplaceField:
    def __init__(self, table=None, field=None, external_condition=str()):
        self.__table = table
        self.__field = field
        self.__external_condition = external_condition

    @property
    def table(self):
        return self.__table

    @table.setter
    def table(self, table):
        self.__table = table

    @property
    def field(self):
        return self.__field

    @field.setter
    def field(self, field):
        self.__field = field

    @property
    def external_condition(self):
        return self.__external_condition

    @external_condition.setter
    def external_condition(self, external_condition):
        self.__external_condition = external_condition
