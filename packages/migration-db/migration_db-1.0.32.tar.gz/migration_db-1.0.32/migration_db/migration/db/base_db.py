# !/usr/bin/python3
# -*- coding:utf-8 -*-
"""
@Author: xiaodong.li
@Time: 2/5/2021 8:13 PM
@Description: Description
@File: BaseDb.py
"""
from ..core.models.config import Config
from ..lib.my_db import MyDB


class BaseDb:

    def __init__(self, data_source):
        self.data_source = data_source

    def _my_db(self):
        return MyDB(Config(**self.data_source))

    def fetchall(self, sql, params=None):
        return self._my_db().fetchall(sql, params)

    def fetchone(self, sql, params=None):
        return self._my_db().fetchone(sql, params)

    def fetchone_and_get_value(self, sql, item=str(), params=None):
        data = self.fetchone(sql, params) or dict()
        if len(data) == 1:
            return list(data.values())[0]
        else:
            raise Exception("The item({0}) does not exist.".format(item))

    def get_old_data(self):
        pass

    def get_table_count(self):
        res = self.fetchall("SHOW FULL TABLES  WHERE Table_type = 'BASE TABLE';")
        return res and len(res) or 0

    def get_all_tables(self):
        items = self.fetchall("SHOW FULL TABLES  WHERE Table_type = 'BASE TABLE';")
        return items and [list(item.values())[0] for item in items] or list()

    def insert(self, table_name, table_data):
        return self._my_db().insert(table_name, table_data)

    def execute(self, sql, params=None):
        return self._my_db().execute(sql, params)

    def get_all_process_id(self, database):
        items = self.fetchall(f'SELECT * FROM information_schema.`PROCESSLIST` WHERE db="{database}"') or list()
        print(f"There are {len(items)} database ({database}) processes")
        return [f"KILL {item.get('ID')};" for item in items]

    def get_all_views(self):
        items = self.fetchall("SHOW FULL TABLES WHERE TABLE_TYPE LIKE 'VIEW';")
        return items and [list(item.values())[0] for item in items] or list()

    def drop_all_views(self):
        views = self.get_all_views()
        for view in views:
            self.execute(f"DROP VIEW {view};")

    def truncate_table(self, table_name):
        return self.execute(f"TRUNCATE {table_name};")

    def count_table(self, table_name):
        item = self.fetchone(f"SELECT COUNT(*) as count FROM {table_name};") or dict()
        return item.get("count")
