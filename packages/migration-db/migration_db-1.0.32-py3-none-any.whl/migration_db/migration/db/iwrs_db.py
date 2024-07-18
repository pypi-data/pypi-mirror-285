# !/usr/bin/python3
# -*- coding:utf-8 -*-
"""
@Author: xiaodong.li
@Time: 2/10/2023 8:25 PM
@Description: Description
@File: iwrs_db.py
"""
from .base_db import BaseDb


class IwrsDb(BaseDb):

    def __init__(self, data_source):
        super().__init__(data_source)

    def get_study_site_info(self):
        study_dto = self.fetchone("SELECT name, 1 as randomzied FROM eclinical_iwrs_study;")
        items = self.fetchall("SELECT name FROM eclinical_iwrs_site;")
        site_list = [item.get("name") for item in items]
        depots = self.fetchall("SELECT * FROM `eclinical_iwrs_depot`;")
        return dict(study_dto=study_dto, sites=site_list, depots=depots)
