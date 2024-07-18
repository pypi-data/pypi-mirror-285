# !/usr/bin/python3
# -*- coding:utf-8 -*-
"""
@Author: xiaodong.li
@Time: 2/5/2021 4:16 PM
@Description: Description
@File: parse.py
"""

from jinja2 import Environment, FileSystemLoader

from ...lib.path import template_path


def parse(template_name, **kwargs):
    env = Environment(loader=FileSystemLoader(template_path()))
    tpl = env.get_template(f"{template_name}.j2")
    return tpl.render(**kwargs)
