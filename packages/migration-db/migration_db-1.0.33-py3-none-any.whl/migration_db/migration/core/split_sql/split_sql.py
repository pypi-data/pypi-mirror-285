# !/usr/bin/python3
# -*- coding:utf-8 -*-
"""
@Author: xiaodong.li
@Time: 12/21/2022 4:22 PM
@Description: Description
@File: split_sql.py
"""
import re
from enum import Enum

from ...lib.constant import App

REGEX_INSERT_INTO = r"INSERT INTO (()|(`)){0}(()|(`)) VALUES \(.*"
REGEX_CREATE_TABLE = r"CREATE TABLE (()|(`)){0}(()|(`)) \(.*"
RELATE_INFOS = ["INSERT INTO", "CREATE TABLE", "eclinical_study_site", "eclinical_study", "eclinical_iwrs_site",
                "eclinical_iwrs_study"]
SPLIT_FLAG = b";\n"


class RegexType:
    complete = "Complete"
    incomplete = "Incomplete"


class EDCRegexEnum(Enum):

    def __init__(self, pattern, flags, table):
        self.pattern = pattern
        self.flags = flags
        self.table = table

    study_site_insert_into = REGEX_INSERT_INTO.format("eclinical_study_site"), re.I, "eclinical_study_site"
    study_insert_into = REGEX_INSERT_INTO.format("eclinical_study"), re.I, "eclinical_study"
    study_site_create_table = REGEX_CREATE_TABLE.format("eclinical_study_site"), re.I | re.M, "eclinical_study_site"
    study_create_table = REGEX_CREATE_TABLE.format("eclinical_study"), re.I | re.M, "eclinical_study"


class IWRSRegexEnum(Enum):

    def __init__(self, pattern, flags, table):
        self.pattern = pattern
        self.flags = flags
        self.table = table

    study_site_insert_into = REGEX_INSERT_INTO.format("eclinical_iwrs_site"), re.I, "eclinical_iwrs_site"
    study_insert_into = REGEX_INSERT_INTO.format("eclinical_iwrs_study"), re.I, "eclinical_iwrs_study"
    study_site_create_table = REGEX_CREATE_TABLE.format("eclinical_iwrs_site"), re.I | re.M, "eclinical_iwrs_site"
    study_create_table = REGEX_CREATE_TABLE.format("eclinical_iwrs_study"), re.I | re.M, "eclinical_iwrs_study"

    depot_insert_into = REGEX_INSERT_INTO.format("eclinical_iwrs_depot"), re.I, "eclinical_iwrs_depot"
    depot_create_table = REGEX_CREATE_TABLE.format("eclinical_iwrs_depot"), re.I | re.M, "eclinical_iwrs_depot"


class DesignRegexEnum(Enum):

    def __init__(self, pattern, flags, table):
        self.pattern = pattern
        self.flags = flags
        self.table = table

    study_insert_into = REGEX_INSERT_INTO.format("eclinical_study"), re.I, "eclinical_study"
    study_create_table = REGEX_CREATE_TABLE.format("eclinical_study"), re.I | re.M, "eclinical_study"


class StudySiteSQLDto:

    def __init__(self, sql=None, tables=None, has_generate=False):
        self.sql = sql
        self.tables = tables or list()
        self.has_generate = has_generate


def read_in_block(file_path):
    block_size = 1024
    with open(file_path, "rb") as f:
        pre_items = []
        while True:
            block = f.read(block_size)  # 每次读取固定长度到内存缓冲区
            if block:
                result = []
                if SPLIT_FLAG in block:
                    has_split_symbol = True
                else:
                    has_split_symbol = False
                if len(pre_items) > 0:
                    if has_split_symbol:
                        result.append(pre_items[-1] + block.split(SPLIT_FLAG)[0])
                        result.extend(block.split(SPLIT_FLAG)[1:-1])
                        pre_items = block.split(SPLIT_FLAG)
                    else:
                        pre_items = [pre_items[-1] + block]
                else:
                    if has_split_symbol:
                        result.extend(block.split(SPLIT_FLAG)[:-1])
                        pre_items = block.split(SPLIT_FLAG)
                    else:
                        pre_items = [block]
                yield result
            else:
                return  # 如果读取到文件末尾，则退出


def generate_study_site_sql_dto(file_path, app) -> StudySiteSQLDto or None:
    study_site_dto = StudySiteSQLDto()
    generate_sql_list = list()
    for block in read_in_block(file_path):
        for item in block:
            try:
                text = item.decode("utf-8").replace("\n", "").replace("\r", "")
                if all(term not in text for term in RELATE_INFOS):
                    continue
                if len(generate_sql_list) >= 6:  # //todo 校验跳出循环的条件
                    break
                if app == App.edc:
                    regex_enum = EDCRegexEnum
                elif app == App.iwrs:
                    regex_enum = IWRSRegexEnum
                elif app == App.design:
                    regex_enum = DesignRegexEnum
                else:
                    continue
                for regex in regex_enum:
                    m = re.match(regex.pattern, text, regex.flags)
                    if m:
                        generate_sql_list.append(item + SPLIT_FLAG)
                        if study_site_dto.has_generate is False:
                            study_site_dto.has_generate = True
                        if regex.table not in study_site_dto.tables:
                            study_site_dto.tables.append(regex.table)
                        break
            except BaseException as e:
                print(e)
        if len(generate_sql_list) >= 6:  # //todo 校验跳出循环的条件
            break
    study_site_dto.sql = b"".join(generate_sql_list)
    return study_site_dto.has_generate is True and study_site_dto or None
