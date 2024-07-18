# !/usr/bin/python3
# -*- coding:utf-8 -*-
"""
@Author: xiaodong.li
@Time: 6/27/2022 10:28 AM
@Description: Description
@File: redis_biz.py
"""
from common_utils.read_file import connection_factory

from ..lib.handle_redis import delete_all_key
from ..lib.path import get_redis_detail_path


class RedisBiz:

    def __init__(self, host, app, study_id, app_env):
        self.data = connection_factory(get_redis_detail_path()).data.get(host)
        self.app = app
        self.study_id = study_id
        self.app_env = app_env

    def delete(self, is_public_network):
        if self.data is not None:
            if not self.data.get("host"):
                external_host = self.data.pop("external_host")
                intranet_host = self.data.pop("intranet_host")
                if is_public_network:
                    self.data.update(dict(host=external_host))
                else:
                    self.data.update(dict(host=intranet_host))
            self.delete_redis_key(self.app, self.study_id, app_env=self.app_env, **self.data)

    def delete_redis_key(self, app, study_id, host=None, app_env=None, port=6379, password="Admin123"):
        string = f"study:{study_id}"
        if app == "edc" and app_env:
            string = f"study:{study_id}:env:{app_env}"
        try:
            delete_all_key(self.app_code_dict().get(app, None), string, host, port, password)
        except Exception as e:
            print(e)

    @staticmethod
    def app_code_dict():
        return dict(design=3, edc=4, iwrs=5)
