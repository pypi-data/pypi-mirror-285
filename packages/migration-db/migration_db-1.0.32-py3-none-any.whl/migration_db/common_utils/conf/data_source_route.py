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

from .config import Config


class DataSourceRoute:

    @staticmethod
    def _build_config(section, use_config_obj=True):
        cfp = configparser.ConfigParser()
        config_path = os.path.join(os.path.dirname(os.path.realpath(__file__)), "data_source.ini")
        cfp.read(config_path)
        sections = cfp.sections()
        if section not in sections:
            raise Exception("error")
        host = cfp.get(section, "host")
        user_name = cfp.get(section, "user")
        port = cfp.get(section, "port")
        password = cfp.get(section, "password")
        if use_config_obj:
            conf = Config(host, user_name, password, port)
        else:
            conf = dict(host=host, port=port, user=user_name, password=password)
        return conf

    def build_config(self, section, database=None, use_config_obj=True):
        conf = self._build_config(section, use_config_obj)
        if database is not None:
            if isinstance(conf, Config):
                conf.database = database
            else:
                conf["database"] = database
        return conf

    def dev03(self, database=None):
        return self.build_config("dev03", database)

    def dev04(self, database=None):
        return self.build_config("dev04", database)

    def dev01(self, database=None):
        return self.build_config("dev01", database)

    def test01(self, database=None):
        return self.build_config("test01", database)

    def dev02(self, database=None):
        return self.build_config("dev02", database)

    def localhost(self, database=None):
        return self.build_config("localhost", database)

    def decommission(self, database=None):
        return self.build_config("decommission", database)
