# !/usr/bin/python3
# -*- coding:utf-8 -*-
"""
@Author: xiaodong.li
@Time: 7/26/2023 2:18 PM
@Description: Description
@File: incremental_sql.py
"""
import os
import shutil
import tempfile
import time
from pathlib import Path

from slicing.constant import ListFileInfo
from slicing.factory import SliceFactory
from slicing.info.file_info_list import FileInfoList
from werkzeug.datastructures import FileStorage

from common_utils.calc_time import calc_func_time
from common_utils.constant import BizSqlType, AppEnum, HierarchyLevel
from common_utils.file import hash_file
from common_utils.format_time import now_utc
from common_utils.handle_str import ParseBizSqlForAppInfo
from common_utils.path import initial_sql_dir_path, initial_table_dir_path, incremental_sql_dir_path
from common_utils.read_file import connect_to
from common_utils.write_file import to_json_file
from .models.file_detail import FileDetail, AppDetail

SOURCE_FILE = "source"


def get_incremental_sqls():
    incremental_sql_path_dir = incremental_sql_dir_path()
    result = dict(incremental_sql_path_dir=incremental_sql_path_dir)
    for root, dirs, files in os.walk(incremental_sql_path_dir):
        result.update(**{file_dir: AppDetail() for file_dir in dirs})
        file_dir = None
        max_sql_version = None
        max_sql_version_file_name = None
        tmp_result = list()
        file_source_mapping = dict()
        source_file = f"{SOURCE_FILE}.json"
        file_source_obj = connect_to(os.path.join(root, source_file), ignore_error=True)
        if file_source_obj is not None:
            file_source_mapping = file_source_obj.data
        for file in files:
            if file_dir is None:
                for k in result.keys():
                    if root.endswith(k):
                        file_dir = k
                        break
            if file == source_file:
                continue
            file_path = os.path.join(root, file)
            file_detail = FileDetail()
            file_detail.file_path = file_path
            file_detail.file_name = file
            file_detail.file_size = os.path.getsize(file_path)
            file_detail.create_time = os.path.getctime(file_path)
            file_detail.modify_time = os.path.getmtime(file_path)
            file_detail.file_source = file_source_mapping.get(file, str())
            file_detail.file_owner = "system"
            p = ParseBizSqlForAppInfo().parse(file_detail.file_name)
            sql_version = p.version_id
            file_detail.sql_version = sql_version
            tmp_result.append(file_detail)
            if max_sql_version is None:
                max_sql_version = sql_version
                max_sql_version_file_name = file
            else:
                if max_sql_version < sql_version:
                    max_sql_version = sql_version
                    max_sql_version_file_name = file
        tmp_result = sorted(tmp_result, key=lambda x: x.sql_version, reverse=True)
        if file_dir is not None:
            app_detail = result[file_dir]
            app_detail.max_sql_version = max_sql_version
            app_detail.max_sql_version_file_name = max_sql_version_file_name
            app_detail.files.extend(tmp_result)
    return result


def get_incremental_sql_file_content(app, file_name, check_size=False):
    file_path = os.path.join(incremental_sql_dir_path(), app, file_name)
    if os.path.getsize(file_path) > 1 * 1024 * 1024 and check_size is True:
        return "文件内容超过1M，请下载文件查看。"
    else:
        with open(file_path, "r", encoding="utf-8") as f:
            return f.read()


def get_incremental_sql_file(app, file_name):
    result = get_incremental_sqls()
    for k, app_detail in result.items():
        if k == app.lower():
            for file in app_detail.files:
                if file.file_name == file_name:
                    return file
    return None


def get_incremental_sql_file_path(app, file_name):
    file = get_incremental_sql_file(app, file_name)
    return file is not None and file.file_path or None


def get_latest_incremental_sql_file_name(app):
    result = get_incremental_sqls()
    for k, app_detail in result.items():
        if k == app.lower():
            for file in app_detail.files:
                if file.sql_version == app_detail.max_sql_version:
                    return file.file_name
    return None


def save_incremental_sql(app, file_name, data):
    file_path = os.path.join(incremental_sql_dir_path(), app, file_name)
    data.save(file_path)


def get_latest_incremental_sql_version(app):
    result = get_incremental_sqls()
    for k, app_detail in result.items():
        if k == app.lower():
            return app_detail.max_sql_version
    return None


def get_incremental_sql_versions(app):
    result = get_incremental_sqls()
    for k, app_detail in result.items():
        if k == app.lower():
            return [file for file in app_detail.files]
    return list()


def filter_by_pattern(lines, biz_sql_type=BizSqlType.INCREMENTAL.description):
    exclude_map = dict(
        design=["20210313_hengrui_demo", "20210222_henrui_demo"],
        edc=["20210313_hengrui_demo", "20210222_henrui_demo", "20210207_edc_payment_ctms_tmf"],
        iwrs=["20210313_hengrui_demo", "20210222_henrui_demo"],
        ctms=["20210401_hengrui_demo", "20210228_hengrui_demo", "20210207_edc_payment_ctms_tmf"],
        etmf=["20210801_us_dev", "20210331_not_go_live", "20210716_us_dev"],
        pv=["20220828", "20220313"],
        coding=["coding release package template"],
    )
    result = dict()
    for line in lines:
        if line.endswith(".sql") and "uat-us" in line:
            tmp_list = line.split("/")
            file_name = tmp_list[-1]
            p = ParseBizSqlForAppInfo().parse(file_name)
            if p.version_id is None or p.sql_type != biz_sql_type:
                continue
            app = p.app
            if exclude_map.get(app) and any(exclude_item in line for exclude_item in exclude_map.get(app)):
                continue
            file_dto = FileDetail()
            file_dto.file_name = file_name
            file_dto.file_path = line
            if app not in result:
                result.update({app: [file_dto]})
            else:
                result[app].append(file_dto)
    return result


@calc_func_time
def copy_file(destination_path, repository_root, filter_result):
    for app, files in filter_result.items():
        app_dir = os.path.join(destination_path, app)
        os.makedirs(app_dir, exist_ok=True)
        mapping = dict()
        tmp_file_names = list()
        for file_dto in files:
            # 如果存在重名，自动重命名
            file_name = file_dto.file_name
            if file_name not in tmp_file_names:
                tmp_file_names.append(file_name)
            else:
                p = ParseBizSqlForAppInfo().parse(file_name)
                rename_file_name = file_name.replace(str(p.version_id), str(p.version_id + 1))
                if rename_file_name not in tmp_file_names:
                    file_name = rename_file_name
            mapping.update({file_name: file_dto.file_path})
            copy_form_path = os.path.join(repository_root, file_dto.file_path)
            copy_to_path = os.path.join(app_dir, file_name)
            if os.path.exists(copy_form_path) and os.path.exists(copy_to_path):
                if hash_file(copy_form_path) == hash_file(copy_to_path):
                    continue
            shutil.copy2(copy_form_path, copy_to_path)
        # 保存映射关系
        to_json_file(app_dir, SOURCE_FILE, mapping)


def build_initial_tables():
    initial_sql_dir = initial_sql_dir_path()
    for root, dirs, files in os.walk(initial_sql_dir):
        for dir_name in dirs:
            dir_path = os.path.join(initial_sql_dir, dir_name)
            source_file_path = os.path.join(dir_path, f"{SOURCE_FILE}.json")
            if dir_name == AppEnum.CODING.code:
                for hierarchy_level in [HierarchyLevel.COMPANY.level_name, HierarchyLevel.STUDY.level_name]:
                    filename = get_latest_initial_sql_file_name(source_file_path, hierarchy_level)
                    file_path = os.path.join(dir_path, filename)
                    parse_initial_sql_and_build_tables(file_path, dir_name, hierarchy_level)
            else:
                filename = get_latest_initial_sql_file_name(source_file_path)
                file_path = os.path.join(dir_path, filename)
                parse_initial_sql_and_build_tables(file_path, dir_name)


def get_latest_initial_sql_file_name(source_file_path, hierarchy_level=None):
    data = connect_to(source_file_path).data
    filename = None
    max_version_id = None
    for item in data.keys():
        p = ParseBizSqlForAppInfo().parse(item)
        if p.hierarchy_level is not None and hierarchy_level is not None and p.hierarchy_level != hierarchy_level:
            continue
        if max_version_id is None or max_version_id < p.version_id:
            max_version_id = p.version_id
            filename = item
    return filename


def parse_initial_sql_and_build_tables(file_path, app, hierarchy_level=None):
    slice_path = tempfile.mkdtemp()
    task_id = SliceFactory.slice(absolute_file_path=Path(file_path), absolute_out_put_folder=Path(slice_path))
    if task_id is not None:
        task_dir = os.path.join(slice_path, str(task_id))
        file_list = FileInfoList(where=Path(task_dir))
        tables = file_list.table(list_type=ListFileInfo.CREATE)
        tmp_li = [app]
        if hierarchy_level is not None:
            tmp_li.append(hierarchy_level)
        to_json_file(initial_table_dir_path(), "_".join(tmp_li), tables)


def get_initial_tables_path(app, hierarchy_level=None):
    tmp_li = [app]
    if hierarchy_level is not None:
        tmp_li.append(hierarchy_level)
    file_path = os.path.join(initial_table_dir_path(), f"{'_'.join(tmp_li)}.json")
    return file_path


def build_incremental_sql_path(incremental_sql_name, incremental_sql_dir: str = None):
    if incremental_sql_dir is None:
        incremental_sql_dir: str = incremental_sql_dir_path()
    p: ParseBizSqlForAppInfo = ParseBizSqlForAppInfo().parse(incremental_sql_name)
    incremental_extra_path: str = os.path.join(os.path.dirname(incremental_sql_dir), "incremental_extra", p.app)
    return incremental_extra_path


def load_incremental_sql_setting(incremental_sql_name, incremental_sql_dir: str = None):
    source_file_mapping = os.path.join(build_incremental_sql_path(incremental_sql_name, incremental_sql_dir),
                                       "source.json")
    f = connect_to(source_file_mapping, ignore_error=True)
    return f is not None and f.data or dict()


def get_incremental_sql_setting(incremental_sql_name, incremental_sql_dir: str = None):
    data = load_incremental_sql_setting(incremental_sql_name, incremental_sql_dir)
    return data.get(incremental_sql_name)


def save_incremental_sql_setting(incremental_sql_name, incremental_sql_dir: str, data):
    to_json_file(build_incremental_sql_path(incremental_sql_name, incremental_sql_dir), "source", data)


def update_incremental_sql_setting(incremental_sql_name, incremental_sql_dir: str = None, execution_order=None,
                                   ttype=None, name=None):
    data = load_incremental_sql_setting(incremental_sql_name, incremental_sql_dir)
    if incremental_sql_name in data:
        items = data[incremental_sql_name][ttype]
        for item in items:
            if item.get("name") == name:
                item["tag"] = execution_order
                item["time"] = now_utc(time.time())
    save_incremental_sql_setting(incremental_sql_name, incremental_sql_dir, data)


def delete_incremental_sql_setting(incremental_sql_name, incremental_sql_dir: str = None, ttype=None, name=None):
    data = load_incremental_sql_setting(incremental_sql_name, incremental_sql_dir)
    if incremental_sql_name in data:
        items = data[incremental_sql_name][ttype]
        delete_item = None
        for item in items:
            if item.get("name") == name:
                delete_item = item
        if delete_item is not None:
            items.remove(delete_item)
    save_incremental_sql_setting(incremental_sql_name, incremental_sql_dir, data)
    incremental_extra_path: str = build_incremental_sql_path(incremental_sql_name, incremental_sql_dir)
    file_path = os.path.join(incremental_extra_path, name)
    if os.path.exists(file_path):
        os.remove(file_path)


def add_or_update_incremental_sql_setting(incremental_sql_name, incremental_sql_dir: str = None, execution_order=None,
                                          ttype=None, name=None, file=None):
    data = load_incremental_sql_setting(incremental_sql_name, incremental_sql_dir)
    if incremental_sql_name in data:
        items = data[incremental_sql_name][ttype]
        for item in items:
            if item.get("name") == name:
                item["tag"] = execution_order
                item["time"] = now_utc(time.time())
                break
        else:
            items.append({"name": name, "tag": execution_order, "time": now_utc(time.time())})
    else:
        data.update(
            {incremental_sql_name: {ttype: [{"name": name, "tag": execution_order, "time": now_utc(time.time())}]}})
    save_incremental_sql_setting(incremental_sql_name, incremental_sql_dir, data)
    incremental_extra_path: str = build_incremental_sql_path(incremental_sql_name, incremental_sql_dir)
    if isinstance(file, FileStorage):
        file_path = os.path.join(incremental_extra_path, name)
        file.save(file_path)


def has_extra_ttype(incremental_sql_name, incremental_sql_dir: str = None, ttype=None):
    data = load_incremental_sql_setting(incremental_sql_name, incremental_sql_dir)
    flag = False
    if incremental_sql_name in data:
        if ttype in data[incremental_sql_name]:
            if len(data[incremental_sql_name][ttype]) > 0:
                flag = True
    return flag
