# !/usr/bin/python3
# -*- coding:utf-8 -*-
"""
@Author: xiaodong.li
@Time: 5/10/2024 6:22 PM
@Description: Description
@File: migration_db_from_s3.py
"""
import copy
import os
import shutil
import sys
import tempfile
import traceback

sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.realpath(__file__)))))
from common_utils.constant import AppEnum, AppEnvEnum
from common_utils.handle_str import ParseNameForAppInfo
from common_utils.log import Logger
from common_utils.read_file import connect_to
from common_utils.s3.s3 import init_client, build_file_dtos, init_resource, download
from migration.core._migration import Migration
from migration.core.handle_file import handle_archive, handle_sql_file
from migration.lib.constant import MigrationTypeEnum
from migration.lib.path import get_app_config_path


def restore_dbs_from_s3(config: dict, s3_sql_locations: list, prefix: str, bucket: str, app_env: str, schema: str,
                        is_publish_network: bool, ignore_error: bool, incremental_sql_dir: str, update_sql_dir: str,
                        latest_sql_versions: dict = None, assigned_study_id=None, assigned_replace_study_id=None):
    """
    :param config: 数据源信息
    :param s3_sql_locations: s3文件key的列表
    :param prefix: 临时文件夹名称前缀
    :param bucket: s3的bucket名称
    :param app_env: 还原的lifecycle
    :param schema: 指定那个数据库还原，为了拿到study_id
    :param is_publish_network: 连接redis使用
    :param ignore_error: 执行增量脚本时，是否忽略SQL运行时的错误
    :param incremental_sql_dir: 增量文件路径
    :param update_sql_dir: 生成的修改数据库id文件路径
    :param latest_sql_versions: 最新的数据库版本
    :param assigned_study_id: 针对sponsor分库的数据库，本地的study_id，目前只针对ctms、etmf进行处理
    :param assigned_replace_study_id: 针对sponsor分库的数据库，需要替换的study_id
    :return:
    """
    if latest_sql_versions is None:
        latest_sql_versions = dict()
    # config_info.json更新于2024-07-18
    config_info_mapping = connect_to(get_app_config_path()).data
    _s3 = init_client()
    file_dtos = build_file_dtos(_s3, bucket, s3_sql_locations)
    file_dtos = sorted(file_dtos, key=lambda x: x.size)
    download_s3 = init_resource()
    for file_dto in file_dtos:
        # 从S3下载文件到本地
        in_path = tempfile.mkdtemp(prefix=prefix)
        p = ParseNameForAppInfo().parse(file_dto.name)
        if p.app not in latest_sql_versions:
            raise Exception(f"Please configure the latest_sql_version_id of {p.app} in latest_sql_versions.")
        if p.app not in [member.code for member in AppEnum]:
            raise Exception(f"Please configure the app:{p.app} information in AppEnum.")
        p_local = ParseNameForAppInfo().parse(schema)
        if p.app in [AppEnum.CTMS.code, AppEnum.ETMF.code, AppEnum.PV.code]:
            id_ = p_local.id
        elif p.app in [AppEnum.DESIGN.code, AppEnum.EDC.code, AppEnum.IWRS.code]:
            id_ = assigned_study_id or p_local.id
        else:
            raise Exception(f"Please confirm the app:{p.app} id.")
        if p.app == AppEnum.DESIGN.code:
            app_env = AppEnvEnum.DEV.description
        database = "_".join(["eclinical", p.app, app_env, str(id_)])
        try:
            Logger().info(f"File: {file_dto.name} is start.")
            local_sql_path = os.path.join(in_path, file_dto.name)
            download(download_s3, bucket, file_dto.key, local_sql_path)
            if local_sql_path.endswith((".zip", ".gz")):
                local_sql_path = handle_archive(in_path, file_dto.name, True, True)
            elif local_sql_path.endswith((".sql",)):
                local_sql_path = handle_sql_file(in_path, file_dto.name)
            Logger().info(f"{file_dto.name}-{database} is start.")
            tmp_config = copy.deepcopy(config)
            if p.app in [AppEnum.CTMS.code, AppEnum.ETMF.code, AppEnum.PV.code]:
                tmp_assigned_study_id = assigned_study_id
                tmp_assigned_replace_study_id = assigned_replace_study_id
            else:
                tmp_assigned_study_id = None
                tmp_assigned_replace_study_id = None
            m_instance = Migration(database, tmp_config, tmp_assigned_study_id, tmp_assigned_replace_study_id,
                                   local_sql_path, True, True, migration_type=MigrationTypeEnum.MYSQL.code)
            m_instance.run(is_publish_network, config_info_mapping.get(p.app), ignore_error,
                           int(latest_sql_versions.get(p.app)), incremental_sql_dir=incremental_sql_dir,
                           update_sql_dir=update_sql_dir, is_kill_process=False)
            Logger().info(f"Filename:{file_dto.name}-{database} is end.")
        except Exception as e:
            traceback.print_exc()
            Logger().error(f"Filename:{file_dto.name}-{database} is error: {e}.")
            raise Exception(e)
        finally:
            shutil.rmtree(in_path)
