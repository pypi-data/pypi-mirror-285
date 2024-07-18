# !/usr/bin/python3
# -*- coding:utf-8 -*-
"""
@Author: xiaodong.li
@Time: 5/10/2024 4:34 PM
@Description: Description
@File: run_refresh_incremental_sql.py
"""
from common_utils.path import incremental_sql_dir_path
from migration.core.refresh_incremental_sql import refresh_git_incremental_file

if __name__ == '__main__':
    url = "https://git-codecommit.cn-northwest-1.amazonaws.com.cn/v1/repos/eclinical40-document"
    user, pwd = "li.xiaodong-at-268264967141", "h9JRoN5oh6UiGxz6X2+ppx3L0rrNu31Q/9nXP3IgoiM="
    branch_name = 'master'
    incremental_sql_dir = incremental_sql_dir_path()
    refresh_git_incremental_file(url, user, pwd, branch_name, incremental_sql_dir)
#     PermissionError
