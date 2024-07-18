# !/usr/bin/python3
# -*- coding:utf-8 -*-
"""
@Author: xiaodong.li
@Time: 11/7/2022 1:52 PM
@Description: Description
@File: data_source_route.py
"""
import configparser
import os

from eClinical40.models.config import Config
from eClinical40.utils.path import get_conf_path


class StudyInfoRoute:

    @staticmethod
    def _build_config(section):
        cfp = configparser.ConfigParser()
        config_path = os.path.join(get_conf_path(), "study_info.ini")
        cfp.read(config_path)
        sections = cfp.sections()
        if section not in sections:
            raise Exception("error")
        conf = Config()
        conf.host = cfp.get(section, "sponsor")
        conf.user_name = cfp.get(section, "study")
        return conf

    def build_config(self, section, database=None):
        conf = self._build_config(section)
        if database is not None:
            conf.database = database
        return conf

    def dev03(self, database=None):
        return self.build_config("dev03", database)

    def dev01(self, database=None):
        return self.build_config("dev01", database)

    def test01(self, database=None):
        return self.build_config("test01", database)
