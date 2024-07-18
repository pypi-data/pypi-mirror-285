# !/usr/bin/python3
# -*- coding:utf-8 -*-
"""
@Author: xiaodong.li
@Time: 6/27/2022 10:46 AM
@Description: Description
@File: execute_script.py
"""
import os
import time

from common_utils.format_time import now_utc
from common_utils.handle_str import ParseBizSqlForAppInfo, ParseNameForAppInfo
from common_utils.log import Logger
from common_utils.path import incremental_sql_dir_path
from common_utils.read_file import connect_to
from ..db.base_db import BaseDb
from ..lib.constant import TABLE_SCHEMA_HISTORY, IncrementalExtraEnum, ExecutionOrderEnum
from ..lib.mysql_task import MysqlTask
from ..lib.path import common_sql_path


class ExecuteScript:

    def __init__(self, data_source):
        self.data_source = data_source
        db = self.data_source.get("db")
        if db is not None:
            p = ParseNameForAppInfo().parse(db)
            app = p.app
            hierarchy_level = p.hierarchy_level
        else:
            raise Exception("The db is empty.")
        self.app: str = app
        self.hierarchy_level = hierarchy_level

    def execute_incremental_sql(self, ignore_error=False, latest_version=None, incremental_sql_dir=None):
        if incremental_sql_dir is None:
            incremental_sql_dir = incremental_sql_dir_path()
        sql_dir = os.path.join(incremental_sql_dir, self.app)
        all_tables = BaseDb(self.data_source).get_all_tables()
        if TABLE_SCHEMA_HISTORY not in all_tables:
            table_schema_path = os.path.join(common_sql_path(), "{0}.sql".format(TABLE_SCHEMA_HISTORY))
            MysqlTask(**self.data_source).mysql_task(table_schema_path)
        sql = "SELECT script FROM eclinical_schema_history WHERE type='SQL' " \
              "AND success=TRUE ORDER BY installed_rank DESC LIMIT 1;"
        item = BaseDb(self.data_source).fetchone(sql)
        db_max_version = None
        if item is not None:
            script = item.get("script")
            p = ParseBizSqlForAppInfo().parse(script)
            db_max_version = p.version_id
        if db_max_version is None or db_max_version == latest_version:
            return
        version_file_mapping = dict()
        for root, dirs, files in os.walk(sql_dir):
            for sql_name in files:
                if not sql_name.endswith('.sql'):
                    continue
                p = ParseBizSqlForAppInfo().parse(sql_name)
                version = p.version_id
                if (latest_version is not None and version > latest_version) or version <= db_max_version:
                    continue
                hierarchy_level = p.hierarchy_level
                if self.hierarchy_level and hierarchy_level and self.hierarchy_level != hierarchy_level:
                    continue
                version_file_mapping.update({version: sql_name})
        version_file_mapping = sorted(version_file_mapping.items(), key=lambda s: s[0])
        incremental_extra_path = os.path.join(os.path.dirname(incremental_sql_dir), "incremental_extra", self.app)
        incremental_extra_mapping = self.build_incremental_extra_mapping(incremental_extra_path)
        for version, sql_name in version_file_mapping:
            is_execute = False
            try:
                item = BaseDb(self.data_source).fetchone(
                    f"SELECT * FROM eclinical_schema_history WHERE script='{sql_name}';")
            except Exception as e:
                raise Exception(e)
            if not item:
                if db_max_version and version > db_max_version:
                    is_execute = True
                elif db_max_version is None:
                    is_execute = True
                execution_time = 0
                curr_incremental_extra = incremental_extra_mapping.get(sql_name) or dict()
                try:
                    if is_execute:
                        before_incremental_extra = self.get_incremental_extra(curr_incremental_extra,
                                                                              ExecutionOrderEnum.BEFORE.code)
                        self.handle_incremental_extra(before_incremental_extra, incremental_extra_path)
                        start_time = time.time()
                        MysqlTask(**self.data_source).mysql_task(os.path.join(sql_dir, sql_name))
                        execution_time = time.time() - start_time
                        success = True
                    else:
                        continue
                except Exception as e:
                    success = False
                    if ignore_error is False:
                        raise Exception(f"An error occurred while executing {sql_name}: {e}")
                # insert the sql executed record
                if success is False:
                    continue
                max_item = BaseDb(self.data_source).fetchone(
                    f"SELECT installed_rank FROM eclinical_schema_history ORDER BY installed_rank DESC LIMIT 1;")
                max_id = max_item.get('installed_rank') if max_item else 0
                BaseDb(self.data_source).insert(
                    "eclinical_schema_history",
                    dict(installed_rank=max_id + 1, version=version, type="SQL", script=sql_name, checksum=0,
                         execution_time=execution_time, description=f"{self.app} business schema incremental sql",
                         installed_by="test_platform", installed_on=now_utc(time.time()), success=1))
                after_incremental_extra = self.get_incremental_extra(curr_incremental_extra,
                                                                     ExecutionOrderEnum.AFTER.code)
                self.handle_incremental_extra(after_incremental_extra, incremental_extra_path)

    def init_schema_history_and_latest_sql_version(self, latest_version_id):
        if latest_version_id is None:
            return
        all_tables = BaseDb(self.data_source).get_all_tables()
        if TABLE_SCHEMA_HISTORY not in all_tables:
            table_schema_path = os.path.join(common_sql_path(), "{0}.sql".format(TABLE_SCHEMA_HISTORY))
            MysqlTask(**self.data_source).mysql_task(table_schema_path)
        sql = "SELECT * FROM eclinical_schema_history WHERE type='SQL' " \
              "AND success=TRUE ORDER BY installed_rank DESC LIMIT 1;"
        item = BaseDb(self.data_source).fetchone(sql)
        db_max_version = None
        installed_rank = 0
        if item is not None:
            script = item.get("script")
            installed_rank = item.get("installed_rank")
            p = ParseBizSqlForAppInfo().parse(script)
            db_max_version = p.version_id
        flag = False
        if db_max_version is None:
            flag = True
        elif db_max_version < latest_version_id:
            flag = True
        if flag:
            # insert the latest sql_version
            sql_name = f"V{latest_version_id}__{self.app}_business_schema_incremental_sql.sql"
            BaseDb(self.data_source).insert(
                "eclinical_schema_history",
                dict(installed_rank=installed_rank + 1, version=latest_version_id, type="SQL", script=sql_name,
                     checksum=0, execution_time=0, description=f"{self.app} business schema incremental sql",
                     installed_by="test_platform", installed_on=now_utc(time.time()), success=1))

    @staticmethod
    def build_incremental_extra_mapping(incremental_extra_path):
        factory = connect_to(os.path.join(incremental_extra_path, "source.json"), ignore_error=True)
        return factory is not None and factory.data or dict()

    @staticmethod
    def get_incremental_extra(curr_incremental_extra, tag):
        incremental_extra = dict()
        for k, items in curr_incremental_extra.items():
            incremental_extra_list = list()
            for item in items:
                if item.get("tag") == tag:
                    incremental_extra_list.append(item)
            if len(incremental_extra_list) > 0:
                incremental_extra.update({k: incremental_extra_list})
        return incremental_extra

    def handle_incremental_extra(self, incremental_extra, incremental_extra_path):
        for k, items in incremental_extra.items():
            if k == IncrementalExtraEnum.SQL.code:
                for item in items:
                    sql_name = item.get("name")
                    sql_path = os.path.join(incremental_extra_path, sql_name)
                    MysqlTask(**self.data_source).mysql_task(sql_path)
                    Logger().info(f"SQL ({item.get('tag')}-{sql_name}) successfully executed.")
            elif k == IncrementalExtraEnum.API.code:
                # todo
                pass
