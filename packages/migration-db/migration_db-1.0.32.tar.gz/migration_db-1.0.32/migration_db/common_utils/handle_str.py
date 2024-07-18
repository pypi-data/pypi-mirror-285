# !/usr/bin/python3
# -*- coding:utf-8 -*-
"""
@Author: xiaodong.li
@Time: 1/9/2024 4:25 PM
@Description: Description
@File: handle_str.py
"""
import re

from .constant import AppEnvEnum, AppEnum, HierarchyLevel, BizSqlType


class ParseNameForAppInfo:

    def __init__(self):
        self.patterns = [
            r"^eclinical_(?P<app>{app})_(?P<env>{env})_(?P<id>\d+)_.*$",
            r"^eclinical_(?P<app>{app})_(?P<env>{env})_(?P<id>\d+)$",
            r"^eclinical_(?P<app>{app})_(?P<env>{env})_(?P<id>\d+)\.(zip|gz)$",
            r"^eclinical_(?P<app>{app})_(?P<hierarchy_level>{hierarchy_level})_(?P<env>{env})_(?P<id>\d+)_.*$",
            r"^eclinical_(?P<app>{app})_(?P<hierarchy_level>{hierarchy_level})_(?P<env>{env})_(?P<id>\d+)$",
            r"^eclinical_(?P<app>{app})_(?P<hierarchy_level>{hierarchy_level})_(?P<env>{env})_(?P<id>\d+)\.(zip|gz)$",
        ]
        self.match_obj = None

    def parse(self, name):
        envs = [member.description for member in AppEnvEnum]
        apps = [member.code for member in AppEnum]
        if AppEnum.ADMIN.code in apps:
            apps.remove(AppEnum.ADMIN.code)
        hierarchy_levels = [HierarchyLevel.COMPANY.level_name, HierarchyLevel.STUDY.level_name]
        pattern_envs = "|".join(envs)
        pattern_apps = "|".join(apps)
        pattern_hierarchy_levels = "|".join(hierarchy_levels)
        for pattern in self.patterns:
            pattern = pattern.format(app=pattern_apps, env=pattern_envs, hierarchy_level=pattern_hierarchy_levels)
            match_obj = re.match(pattern, name)
            if match_obj:
                self.match_obj = match_obj
                break
        return self

    @property
    def app(self):
        return self.__get_value_from_match_obj("app")

    @property
    def app_env(self):
        return self.__get_value_from_match_obj("env")

    @property
    def id(self):
        _id = self.__get_value_from_match_obj("id")
        if type(_id) is str and _id.isdigit():
            return int(_id)
        return _id

    @property
    def hierarchy_level(self):
        return self.__get_value_from_match_obj("hierarchy_level")

    def __get_value_from_match_obj(self, key):
        if self.match_obj is not None:
            if key in self.match_obj.groupdict():
                return self.match_obj.group(key)
        return None


class ParseBizSqlForAppInfo:
    """
    解析business sql，返回app，version_id，hierarchy_level信息
    """
    patterns = [
        r"^V(?P<version_id>[\d]+)__(?P<app>{app})_business_(?P<sql_type>{sql_type})_sql.sql$",
        r"^V(?P<version_id>[\d]+)__(?P<app>{app})_business_schema_(?P<sql_type>{sql_type})_sql.sql$",
        r"^V(?P<version_id>[\d]+)__(?P<app>{app})_(?P<hierarchy_level>{hierarchy_level})_"
        r"business_(?P<sql_type>{sql_type})_sql.sql$",
        r"^V(?P<version_id>[\d]+)__(?P<app>{app})_(?P<hierarchy_level>{hierarchy_level})_"
        r"business_schema_(?P<sql_type>{sql_type})_sql.sql$",
    ]

    def __init__(self):
        self.match_obj = None

    def parse(self, name):
        apps = [member.code for member in AppEnum]
        if AppEnum.ADMIN.code in apps:
            apps.remove(AppEnum.ADMIN.code)
        hierarchy_levels = [HierarchyLevel.COMPANY.level_name, HierarchyLevel.STUDY.level_name]
        pattern_sql_type = "|".join([member.description for member in BizSqlType])
        pattern_apps = "|".join(apps)
        pattern_hierarchy_levels = "|".join(hierarchy_levels)
        for pattern in self.patterns:
            pattern = pattern.format(app=pattern_apps, hierarchy_level=pattern_hierarchy_levels,
                                     sql_type=pattern_sql_type)
            match_obj = re.match(pattern, name)
            if match_obj:
                self.match_obj = match_obj
                break
        return self

    @property
    def app(self):
        return self.__get_value_from_match_obj("app")

    @property
    def version_id(self):
        version_id = self.__get_value_from_match_obj("version_id")
        if type(version_id) is str and version_id.isdigit():
            return int(version_id)
        return version_id

    @property
    def sql_type(self):
        return self.__get_value_from_match_obj("sql_type")

    @property
    def hierarchy_level(self):
        return self.__get_value_from_match_obj("hierarchy_level")

    def __get_value_from_match_obj(self, key):
        if self.match_obj is not None:
            if key in self.match_obj.groupdict():
                return self.match_obj.group(key)
        return None
