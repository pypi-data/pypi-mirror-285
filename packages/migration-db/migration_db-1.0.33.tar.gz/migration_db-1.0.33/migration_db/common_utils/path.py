# !/usr/bin/python3
# -*- coding:utf-8 -*-
"""
@Author: xiaodong.li
@Time: 12/23/2020 2:32 PM
@Description: Description
@File: path.py
"""

import os
import time

from common_utils.format_time import now


def _base_path():
    return os.path.dirname(os.path.realpath(__file__))


def root():
    return _base_path()


def compare_two_crf_version_docs():
    return os.path.join(os.path.dirname(root()), "docs", "compare_two_crf_version")


def build_data_docs():
    return os.path.join(os.path.dirname(root()), "docs", "build_data")


def build_biz_sql_docs():
    return os.path.join(os.path.dirname(root()), "docs", "business sql")


def compare_two_crf_version_edc_excel_root():
    return os.path.join(compare_two_crf_version_docs(), "edc", "excel")


def compare_two_crf_version_edc_json_root():
    return os.path.join(compare_two_crf_version_docs(), "edc", "json")


def edc_compare_result_path(database, _time=None):
    return os.path.join(compare_two_crf_version_edc_json_root(), database, _time or now(time.time()), "compare")


def edc_duplicate_result_path(database=None, _time=None):
    return os.path.join(compare_two_crf_version_edc_json_root(), database, _time or now(time.time()), "duplicate_data")


def generate_subject_sample_data_path():
    return os.path.join(build_data_docs(), "generate_subject_sample_data")


def generate_form_dto_json_path():
    return os.path.join(build_data_docs(), "form_dto", "json")


def generate_form_dto_path():
    return os.path.join(build_data_docs(), "form_dto")


def initial_sql_dir_path():
    return os.path.join(build_biz_sql_docs(), "initial")


def initial_table_dir_path():
    return os.path.join(build_biz_sql_docs(), "initial tables")


def incremental_sql_dir_path():
    return os.path.join(build_biz_sql_docs(), "incremental")


def update_sql_dir_path():
    return os.path.join(build_biz_sql_docs(), "update_sql")


def build_tmp_docs():
    return os.path.join(os.path.dirname(root()), "docs", "tmp")
