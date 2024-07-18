# !/usr/bin/python3
# -*- coding:utf-8 -*-
"""
@Author: xiaodong.li
@Time: 6/27/2022 11:02 AM
@Description: Description
@File: base.py
"""

from common_utils.constant import HierarchyLevel
from common_utils.handle_str import ParseNameForAppInfo

from .switch_data_source import SwitchDataSource
from ..db.admin_db import AdminDb


class Base:

    def __init__(self, database, data_source, assigned_study_id=None, is_switch_data_source=True):
        self.study_id = assigned_study_id  # 需要处理的study的id
        self.sponsor_id = None  # 需要处理的study所在sponsor的id
        self.env_id = None
        self.company_id = None
        self.system_id = None
        self.system = None
        self.app_env = None
        self.database = database
        self.data_source = data_source
        self.app_db_route = SwitchDataSource(database, data_source, is_switch_data_source).get()

    def init_args(self):
        p = ParseNameForAppInfo().parse(self.database)
        self.system, self.app_env, tmp_id = p.app, p.app_env, p.id
        self.system_id = AdminDb(self.data_source).get_system_id(self.system)
        if p.hierarchy_level == HierarchyLevel.COMPANY.level_name:
            # self.sponsor_id = 0
            # self.study_id = 0
            self.company_id = p.id
            if self.sponsor_id is None and self.study_id is not None:
                self.sponsor_id = AdminDb(self.data_source).get_sponsor_id(self.study_id)
        else:
            is_route_by_study = AdminDb(self.data_source).is_db_route_by_study(self.system)
            self.study_id = is_route_by_study and tmp_id or self.study_id or 0
            self.sponsor_id = not is_route_by_study and tmp_id or AdminDb(self.data_source).get_sponsor_id(
                self.study_id)
            self.company_id = AdminDb(self.data_source).get_company_id(self.sponsor_id)
        self.env_id = AdminDb(self.data_source).get_env_id(self.company_id, self.app_env)
