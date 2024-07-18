# !/usr/bin/python3
# -*- coding:utf-8 -*-
"""
@Author: xiaodong.li
@Time: 5/17/2023 5:26 PM
@Description: Description
@File: mysql_shell.py
"""
import os
import subprocess

from .handle_str import escape_symbol
from ..docs.template.parse import parse
from ..lib.path import build_sql_file_parent_path


class MysqlShellTask:

    def __init__(self, host, port, password, user, db=None):
        self.host = host
        self.port = port
        self.user = user
        self.password = password
        self.db = db or ""
        self.threads = 16

    def __uri(self, is_display=True):
        return f"--uri={self.user}:{is_display and self.password or '******'}@{self.host}:{self.port}"

    @staticmethod
    def __execute_cmd(cmd):
        exitcode, data = subprocess.getstatusoutput(cmd)
        if exitcode != 0:
            raise Exception(data)

    def __backup_cmd_be(self, dir_path, is_display=True):
        items = ["mysqlsh",
                 "--no-defaults",
                 self.__uri(is_display),
                 '-C', 'True',
                 '--compression-algorithms=zstd',
                 '--', 'util', 'dump-schemas', self.db,
                 f'--outputUrl="{escape_symbol(dir_path)}"']
        return " ".join(items)

    def __restore_cmd_be(self, dir_path, is_display=True):
        items = ["mysqlsh",
                 "--no-defaults",
                 self.__uri(is_display),
                 '-e',
                 "\"util.loadDump('%s', {schema:'%s', resetProgress: true})\"" % (escape_symbol(dir_path), self.db)]
        return " ".join(items)

    def __get_cmd_path(self, template, dir_path, generate_file=True):
        cmd = parse(template, dto=self.__dict__, dir_path=dir_path)
        sql_file_parent_path = build_sql_file_parent_path(self.host)
        os.makedirs(sql_file_parent_path, exist_ok=True)
        cmd_file_path = build_sql_file_parent_path(sql_file_parent_path, f"{self.db}_{template}.cmd")
        if generate_file:
            with open(cmd_file_path, "w", encoding="utf-8") as f:
                f.write(cmd)
        return cmd_file_path

    def __get_cmd(self, template, dir_path, generate_file=True):
        cmd_file_path = self.__get_cmd_path(template, escape_symbol(dir_path), generate_file)
        include_no_defaults = True
        # include_no_defaults = False
        return " ".join(["mysqlsh", include_no_defaults and "--no-defaults" or "", f'--file={cmd_file_path}'])

    def __backup_cmd(self, dir_path, generate_file=True):
        return self.__get_cmd("mysql-shell-dump", escape_symbol(dir_path), generate_file)

    def __restore_cmd(self, dir_path, generate_file=True):
        return self.__get_cmd("mysql-shell-load-dump", escape_symbol(dir_path), generate_file)

    def backup_cmd(self, dir_path):
        return self.__backup_cmd(dir_path, generate_file=False)

    def restore_cmd(self, dir_path):
        return self.__restore_cmd(dir_path, generate_file=False)

    def backup_task(self, dir_path):
        cmd = self.__backup_cmd(dir_path)
        return self.__execute_cmd(cmd)

    def restore_task(self, dir_path):
        cmd = self.__restore_cmd(dir_path)
        return self.__execute_cmd(cmd)
