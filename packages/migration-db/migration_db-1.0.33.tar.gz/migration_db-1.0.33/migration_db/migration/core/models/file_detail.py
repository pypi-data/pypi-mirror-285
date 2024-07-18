# !/usr/bin/python3
# -*- coding:utf-8 -*-
"""
@Author: xiaodong.li
@Time: 7/26/2023 2:27 PM
@Description: Description
@File: file_detail.py
"""


class FileDetail:

    def __init__(self):
        self.file_name = None
        self.file_size = None
        self.create_time = None
        self.modify_time = None
        self.file_owner = None
        self.file_path = None
        self.latest = False
        self.is_draft = False
        self.sql_version = None
        self.content = None
        self.file_source = None
        self.extra_sql = False
        self.extra_api = False


class AppDetail:
    def __init__(self):
        self.max_sql_version = None
        self.max_sql_version_file_name = None
        self.files = list()
