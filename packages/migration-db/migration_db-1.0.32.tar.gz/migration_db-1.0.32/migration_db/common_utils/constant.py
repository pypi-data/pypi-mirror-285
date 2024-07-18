# !/usr/bin/python3
# -*- coding:utf-8 -*-
"""
@Author: xiaodong.li
@Time: 1/9/2024 4:26 PM
@Description: Description
@File: constant.py
"""
from enum import unique, Enum


@unique
class AppEnvEnum(Enum):

    def __init__(self, code, description):
        self.code = code
        self.description = description

    DEV = ("DEV", "dev")
    UAT = ("UAT", "uat")
    PROD = ("PROD", "prod")


@unique
class HierarchyLevel(Enum):

    def __init__(self, code, level_name):
        self.code = code
        self.level_name = level_name

    COMPANY = (1, "company")
    SPONSOR = (2, "sponsor")
    STUDY = (3, "study")


@unique
class AppEnum(Enum):

    def __init__(self, system_id, code, description):
        self.id = system_id
        self.code = code
        self.description = description

    ADMIN = (1, "admin", "ADMIN")
    CTMS = (2, "ctms", "CTMS")
    ETMF = (3, "etmf", "eTMF")
    DESIGN = (4, "design", "DESIGN")
    EDC = (5, "edc", "EDC")
    IWRS = (6, "iwrs", "IWRS")
    E_CONSENT = (7, "econsent", "eConsent")
    PV = (8, "pv", "PV")
    CODING = (10, "coding", "CODING")
    IMAGING = (11, "imaging", "IMAGING")


@unique
class BizSqlType(Enum):

    def __init__(self, code, description):
        self.code = code
        self.description = description

    INITIAL = (1, "initial")
    INCREMENTAL = (2, "incremental")
