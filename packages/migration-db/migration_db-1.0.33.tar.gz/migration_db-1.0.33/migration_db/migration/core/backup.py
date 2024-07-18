# !/usr/bin/python3
# -*- coding:utf-8 -*-
"""
@Author: xiaodong.li
@Time: 5/6/2024 9:54 AM
@Description: Description
@File: backup.py
"""
import os
import sys
import zipfile

sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.realpath(__file__)))))
from migration.core.execute_script import ExecuteScript
from migration.lib.mysql_task import MysqlTask


def backup(dir_path: str, sql_name, is_compress=False, data_source=None):
    if not sql_name.endswith(".sql"):
        sql = sql_name + ".sql"
    else:
        sql = sql_name
    local_sql_path = os.path.join(dir_path, sql)
    if data_source is None:
        raise Exception("Please set the data source.")
    MysqlTask(**data_source).mysqldump_task(local_sql_path)
    if is_compress is True:
        zip_backup_path: str = os.path.join(dir_path, sql_name + ".zip")
        with zipfile.ZipFile(zip_backup_path, "w", zipfile.ZIP_DEFLATED) as zipf:
            zipf.write(local_sql_path, arcname=sql)
        if os.path.exists(local_sql_path):
            os.remove(local_sql_path)
    print("Back up database successfully.")


def mgmt_schema_history_and_backup(dir_path: str, sql, is_compress, data_source, latest_version_id):
    ExecuteScript(data_source).init_schema_history_and_latest_sql_version(latest_version_id)
    backup(dir_path, sql, is_compress, data_source)
