# !/usr/bin/python3
# -*- coding:utf-8 -*-
"""
@Author: xiaodong.li
@Time: 2/4/2021 8:25 PM
@Description: Description
@File: edc_db.py
"""

from .base_db import BaseDb


class EdcDb(BaseDb):

    def __init__(self, data_source):
        super().__init__(data_source)

    def get_old_data(self):
        try:
            study_dto = self.fetchone("SELECT id, name FROM eclinical_study;")
            site_dto = self.fetchall("SELECT id, code, FALSE as used FROM eclinical_study_site;")
            role_dto = self.fetchall("""
            SELECT role_id, role_name, FALSE as used FROM eclinical_manual_query_reply GROUP BY role_id, role_name
            UNION
            SELECT role_id, role_name, FALSE as used FROM eclinical_system_query_reply GROUP BY role_id, role_name""")
        except Exception as e:
            raise Exception(e)
        return dict(study_dto=study_dto, site_dto=site_dto, role_dto=role_dto)

    def get_study_site_info(self):
        study_dto = self.fetchone("SELECT name, randomzied FROM eclinical_study;")
        items = self.fetchall("SELECT code FROM eclinical_study_site;")
        site_list = [item.get("code") for item in items]
        return dict(study_dto=study_dto, sites=site_list)
