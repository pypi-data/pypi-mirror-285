# !/usr/bin/python3
# -*- coding:utf-8 -*-
"""
@Author: xiaodong.li
@Time: 8/30/2022 10:30 AM
@Description: Description
@File: run_table_action.py
"""
from migration.core.build_update_sql import BuildUpdateSQL
from migration.core.handle_table_action import handle_actions
from migration.helper.run_edc import get_data
from migration.db.base_db import BaseDb

if __name__ == '__main__':
    res = list()
    data_base = "eclinical_design_dev_820"
    test_platform = dict(host="localhost", port=3306, db="eclinical_test_platform", password="admin123",
                         user="root")
    table_actions = BaseDb(test_platform).fetchall(
        f"SELECT * FROM eclinical_table_action WHERE is_delete=FALSE AND system_id=4;") or list()
    # data_source = dict(host="localhost", port=3306, db="eclinical_test_platform", password="admin123",
    #                    user="root")
    data_source = {"host": "dev-01.c9qe4y0vrvda.rds.cn-northwest-1.amazonaws.com.cn", "port": 3306, "user": "root",
                   "password": "3fgRCcB72Px1FvBfDBNL"}
    data = get_data(test_platform, 5)
    build_update_sql = BuildUpdateSQL(data_base, data_source)
    build_update_sql.table_field_mapping = build_update_sql.build_table_field_mapping(data, table_actions)
    a = handle_actions(table_actions, build_update_sql.all_tables, build_update_sql.table_field_mapping)
    print(a)
