# !/usr/bin/python3
# -*- coding:utf-8 -*-
"""
@Author: xiaodong.li
@Time: 6/17/2024 10:38 AM
@Description: Description
@File: run.py
"""
from migration.core.incremental_sql import get_incremental_sql_setting, update_incremental_sql_setting, \
    delete_incremental_sql_setting

if __name__ == '__main__':
    a = get_incremental_sql_setting("V80__edc_business_schema_incremental_sql.sql",
                                    r"/docs/business sql/incremental_extra")
    print(a)
    update_incremental_sql_setting("V80__edc_business_schema_incremental_sql.sql",
                                   r"/docs/business sql/incremental_extra", "Before", "SQL",
                                   "update_audit_trail_sql.sql")
    delete_incremental_sql_setting("V80__edc_business_schema_incremental_sql.sql",
                                   r"/docs/business sql/incremental_extra", "API",
                                   "update_audit_trail_sql.sql")
