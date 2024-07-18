# !/usr/bin/python3
# -*- coding:utf-8 -*-
"""
@Author: xiaodong.li
@Time: 2021/8/5 10:11
@Description: Description
@File: constant.py
"""
from enum import Enum, unique

OR_PLACEHOLDER = "||"
AND_PLACEHOLDER = "&&"
NEWLINE_PLACEHOLDER_PATTERN = "\r\n|\n"
MAPPING_DATA = "##MAPPING_DATA##"


class App:
    edc = "edc"
    iwrs = "iwrs"
    design = "design"
    etmf = "etmf"


class DataType:
    int = 1
    string = 2


TABLE_SCHEMA_HISTORY = "eclinical_schema_history"


@unique
class ValTypeEnum(Enum):

    def __init__(self, code, val, description):
        self.code = code
        self.val = val
        self.description = description

    STUDY_ID = (3, None, "study_id")
    SPONSOR_ID = (4, None, "sponsor_id")
    ENV_ID = (6, None, "env_id")
    ASSIGNED_REPLACE_STUDY_ID = (7, None, "assigned_replace_study_id")
    IS_NOT_NULL = (8, "IS NOT NULL", "IS NOT NULL")
    STUDY = (9, "study", "study")
    PV_RECORD = (10, None, "pv.eclinical_entry_form_item_record.current_value")
    COMPANY_ID = (11, None, "company_id")
    ID_REPLACE_VALUE = (12, "@replace_value", "replace_value")
    STRING_REPLACE_VALUE = (13, "CONVERT(@replace_value USING utf8mb4) COLLATE utf8mb4_general_ci", "replace_value")
    SITE = (14, "site", "site")
    SITE_ID = (15, MAPPING_DATA, "site_id")
    FALSE = (99, False, "False")
    TRUE = (100, True, "True")


@unique
class AdminFieldEnum(Enum):

    def __init__(self, _id, code):
        self.id = _id
        self.code = code

    SITE_CODE = (1, "site_code")
    SITE_ID = (2, "site_id")
    STUDY_ID = (3, "study_id")
    SPONSOR_ID = (4, "sponsor_id")
    STUDY_NAME = (5, "study_name")


@unique
class TableActionEnum(Enum):

    def __init__(self, _id, description):
        self.id = _id
        self.description = description

    SET_FIELD_VALUE_TO_NULL = (1, "Set the value of the field to null")
    DELETE_ALL_DATA_IN_THE_TABLE = (2, "Delete all the data in the table")


@unique
class MigrationTypeEnum(Enum):

    def __init__(self, code, description):
        self.code = code
        self.description = description

    MYSQL = ("mysql", "migration by mysql")
    MYSQL_SHELL = ("mysqlsh", "migration by mysqlsh")
    MYSQL_CONNECTOR = ("mysql_connector", "migration by mysql-connector-python")


@unique
class IncrementalExtraEnum(Enum):

    def __init__(self, code, description):
        self.code = code
        self.description = description

    SQL = ("SQL", "Execute SQL files to process historical data")
    API = ("API", "Call the interface to process historical data")


@unique
class ExecutionOrderEnum(Enum):

    def __init__(self, code, description):
        self.code = code
        self.description = description

    BEFORE = ("Before", "Executes the script before executing the incremental script.")
    AFTER = ("After", "Execute the script after the incremental script has been executed.")
