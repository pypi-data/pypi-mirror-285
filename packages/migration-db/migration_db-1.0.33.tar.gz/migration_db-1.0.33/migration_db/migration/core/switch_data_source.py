# !/usr/bin/python3
# -*- coding:utf-8 -*-
"""
@Author: xiaodong.li
@Time: 6/24/2022 4:47 PM
@Description: Description
@File: switch_data_source.py
"""
import copy

from common_utils.constant import HierarchyLevel
from common_utils.handle_str import ParseNameForAppInfo
from ..db.admin_db import AdminDb
from ..lib.compareTwoDict import CompareTwoDict, FilterDict


class SwitchDataSource:

    def __init__(self, data_base, data_source, is_switch_data_source=True):
        self.data_base = data_base
        self.data_source = data_source
        self.is_switch_data_source = is_switch_data_source

    def get(self):
        filter_res = None
        app_db_route = None
        data_source = copy.deepcopy(self.data_source)
        try:
            if self.is_switch_data_source is True:
                p = ParseNameForAppInfo().parse(self.data_base)
                if p.hierarchy_level == HierarchyLevel.COMPANY.level_name:
                    sponsor_id = 0

                    study_id = 0
                    company_id = p.id
                else:
                    is_db_route_by_study = AdminDb(data_source).is_db_route_by_study(p.app)
                    study_id = is_db_route_by_study and p.id or 0
                    sponsor_id = not is_db_route_by_study and p.id or AdminDb(data_source).get_sponsor_id(study_id)
                    company_id = AdminDb(data_source).get_company_id(sponsor_id)
                app_db_route = AdminDb(data_source).get_app_route(p.app, p.app_env, sponsor_id, study_id, company_id)
                data_source["db"] = self.data_base
                if app_db_route:
                    res = CompareTwoDict(data_source, app_db_route).main()
                    filter_res = FilterDict(res).main()
        except Exception as e:
            print(e)
        if filter_res and app_db_route:
            return app_db_route
        else:
            data_source["db"] = self.data_base
            return data_source
