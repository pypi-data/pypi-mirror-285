# !/usr/bin/python3
# -*- coding:utf-8 -*-
"""
@Author: xiaodong.li
@Time: 2022/6/19 17:15
@Description: Description
@File: run.py
"""
from common_utils.conf.data_source_route import DataSourceRoute
from migration.core.build_update_sql import BuildUpdateSQL
from migration.db.base_db import BaseDb


def build_external_condition_mapping(test_platform):
    external_condition_fields = BaseDb(test_platform).fetchall(
        f"SELECT * FROM eclinical_condition_field WHERE is_delete=FALSE;") or list()
    mapping = dict()
    for external_condition_field in external_condition_fields:
        system_id = external_condition_field.get("system_id")
        table_name = external_condition_field.get("table_name")
        key = f"{system_id}_{table_name}"
        if mapping.get(key, None) is not None:
            mapping[key].append(external_condition_field)
        else:
            system_table_list = list()
            system_table_list.append(external_condition_field)
            mapping[key] = system_table_list
    return mapping


def get_data(test_platform, system_id):
    return BaseDb(test_platform).fetchall(f"""
                        SELECT d.fields, d.app_source_field, f.data_type, f.code, f.admin_source_field, f.id
                        FROM eclinical_app_field d JOIN eclinical_admin_field f ON d.admin_field_id = f.id
                        WHERE d.system_id={system_id} AND d.is_delete=FALSE ORDER By f.data_type; """)


if __name__ == '__main__':
    data_base = "eclinical_pv_dev_816"

    # data_source = {"host": "dev-03.c9qe4y0vrvda.rds.cn-northwest-1.amazonaws.com.cn", "port": 3306, "user": "root",
    #                "password": "8YTJWOuA7XRK17wRQnw4"}
    data_source = DataSourceRoute().build_config("dev01", use_config_obj=False)
    # data_source = {"host": "test-01.c9qe4y0vrvda.rds.cn-northwest-1.amazonaws.com.cn", "port": 3306, "user": "root",
    #                "password": "HUlWHzVM1J1K0QO1yhhV"}
    # data_source = dict(host="localhost", port=3306, db="eclinical_test_platform", password="admin123",
    #                    user="root")
    test_platform = dict(host="localhost", port=3306, db="eclinical_test_platform", password="admin123",
                         user="root")
    external_condition_fields_mapping = build_external_condition_mapping(test_platform)
    data = get_data(test_platform, 8)
    config_info = dict(data=data, external_condition_fields_mapping=external_condition_fields_mapping)
    _path = BuildUpdateSQL(data_base, data_source, assigned_study_id=820, assigned_replace_study_id=790).build(
        config_info)
    print(_path)
