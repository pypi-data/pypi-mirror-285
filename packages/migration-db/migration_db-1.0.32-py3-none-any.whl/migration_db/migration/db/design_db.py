# !/usr/bin/python3
# -*- coding:utf-8 -*-
"""
@Author: xiaodong.li
@Time: 3/2/2023 8:25 AM
@Description: Description
@File: design_db.py
"""
from .base_db import BaseDb


class DesignDb(BaseDb):

    def __init__(self, data_source):
        super().__init__(data_source)

    def get_study_info(self):
        study_dto = self.fetchone("SELECT name, randomized as randomzied FROM eclinical_study;")
        return dict(study_dto=study_dto)
