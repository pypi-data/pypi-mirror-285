# !/usr/bin/python3
# -*- coding:utf-8 -*-
"""
@Author: xiaodong.li
@Time: 12/23/2020 2:32 PM
@Description: Description
@File: path.py
"""

import os

from common_utils.path import update_sql_dir_path


def root():
    return os.path.dirname(os.path.dirname(os.path.realpath(__file__)))


def docs_path():
    return os.path.join(root(), "docs")


def template_path():
    return os.path.join(docs_path(), "template")


def common_sql_path():
    return os.path.join(docs_path(), "common_sql")


def build_sql_file_parent_path(*args):
    return os.path.join(update_sql_dir_path(), *args)


def get_redis_detail_path():
    return os.path.join(docs_path(), "redis_detail.json")


def get_truncate_db_file_path(app):
    return os.path.join(root(), "db", "truncate_sql", f"{app}.sql")


def get_create_procedure_sql_path():
    return os.path.join(common_sql_path(), "create_procedure.sql")


def get_drop_procedure_sql_path():
    return os.path.join(common_sql_path(), "drop_procedure.sql")


def get_app_config_path():
    return os.path.join(docs_path(), "config_info.json")
