# !/usr/bin/python3
# -*- coding:utf-8 -*-
"""
@Author: xiaodong.li
@Time: 2/4/2021 9:36 PM
@Description: Description
@File: _migration.py
"""
import copy
import os
import queue
import sys
import threading
import time
import traceback

sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.realpath(__file__)))))
from common_utils.calc_time import calc_func_time
from .base import Base
from .build_update_sql import BuildUpdateSQL
from .execute_script import ExecuteScript
from .redis_biz import RedisBiz
from ..db.admin_db import AdminDb
from ..db.base_db import BaseDb
from ..db.design_db import DesignDb
from ..db.edc_db import EdcDb
from ..db.iwrs_db import IwrsDb
from ..lib.constant import App, MigrationTypeEnum
from ..lib.mysql_connector import MysqlConnector
from ..lib.mysql_shell import MysqlShellTask
from ..lib.mysql_task import MysqlTask
from ..lib.path import get_create_procedure_sql_path, get_drop_procedure_sql_path, build_sql_file_parent_path


class Migration(Base):

    def __init__(self, database, data_source=None, assigned_study_id=None, assigned_replace_study_id=None,
                 local_sql_path=None, is_update=True, is_upgrade=False, is_init_args=True, local_path_dir=None,
                 migration_type=MigrationTypeEnum.MYSQL.code, is_generate_update_sql_file=True, slice_path=None,
                 is_restore_all_tables=None, restore_tables=None):
        """

        :param database:
        :param data_source:
        :param assigned_study_id:
        :param assigned_replace_study_id:
        :param local_sql_path:
        :param is_update:
        :param is_upgrade:
        :param is_init_args:
        :param local_path_dir:
        :param migration_type:
        :param is_generate_update_sql_file:
        :param slice_path:
        :param is_restore_all_tables:
        :param restore_tables:
        """
        data_source["db"] = None
        Base.__init__(self, database, data_source, assigned_study_id, is_init_args)
        self.is_update = is_update
        self.is_upgrade = is_upgrade
        self.is_generate_update_sql_file = is_generate_update_sql_file  # 是否生成修改id文件，优先级低于is_update
        if (self.is_update or self.is_upgrade or self.is_generate_update_sql_file) and is_init_args:
            Base.init_args(self)
        self.assigned_study_id = assigned_study_id
        self.assigned_replace_study_id = assigned_replace_study_id
        self.local_sql_path = local_sql_path
        self.local_path_dir = local_path_dir
        self.migration_rate = None
        self.exception = None
        self.migration_type = migration_type
        self.update_sql_path = None  # 修改id文件路径
        self.is_stop = False
        self.slice_path = slice_path
        self.is_restore_all_tables = is_restore_all_tables
        self.restore_tables = restore_tables

    @calc_func_time
    def mysqldump_task(self):
        if self.migration_type == MigrationTypeEnum.MYSQL.code:
            MysqlTask(**self.app_db_route).mysqldump_task(self.local_sql_path)
        elif self.migration_type == MigrationTypeEnum.MYSQL_SHELL.code:
            MysqlShellTask(**self.app_db_route).backup_task(self.local_path_dir)
        print("Back up database successfully.")

    def backup_cmd(self):
        if self.migration_type == MigrationTypeEnum.MYSQL.code:
            pass
        elif self.migration_type == MigrationTypeEnum.MYSQL_SHELL.code:
            return MysqlShellTask(**self.app_db_route).backup_cmd(self.local_path_dir)

    def restore_cmd(self):
        if self.migration_type == MigrationTypeEnum.MYSQL.code:
            pass
        elif self.migration_type == MigrationTypeEnum.MYSQL_SHELL.code:
            return MysqlShellTask(**self.app_db_route).restore_cmd(self.local_path_dir)

    @calc_func_time
    def _restore_database(self, q):
        try:
            if self.migration_type == MigrationTypeEnum.MYSQL.code and self.local_sql_path:
                return MysqlTask(**self.app_db_route).mysql_task(self.local_sql_path)
            elif self.migration_type == MigrationTypeEnum.MYSQL_SHELL.code:
                return MysqlShellTask(**self.app_db_route).restore_task(self.local_path_dir)
            elif self.migration_type == MigrationTypeEnum.MYSQL_CONNECTOR.code:
                return MysqlConnector(**self.app_db_route).restore_from_slice_path(self.slice_path,
                                                                                   self.is_restore_all_tables,
                                                                                   self.restore_tables)
        except Exception as e:
            q.put(e)

    @calc_func_time
    def _update_database(self, config_info, update_sql_dir):
        self.set_update_sql_path(config_info, update_sql_dir)
        if self.update_sql_path is None:
            print("sql path is none.")
        else:
            return MysqlTask(**self.app_db_route).mysql_task(self.update_sql_path)

    @calc_func_time
    def _drop_database(self, is_create_database=True):
        data_source = copy.deepcopy(self.app_db_route)
        data_source["db"] = None
        BaseDb(data_source).execute("DROP DATABASE IF EXISTS `{0}`;".format(self.database))
        if is_create_database is False:
            return
        BaseDb(data_source).execute("CREATE DATABASE /*!32312 IF NOT EXISTS*/ `{0}` /*!40100 "
                                    "DEFAULT CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci */ /*!80016 DEFAULT "
                                    "ENCRYPTION='N' */;".format(self.database))

    def drop_database(self, is_create_database=True):
        return self._drop_database(is_create_database)

    def restore_database(self):
        return self._restore_database()

    def set_update_sql_path(self, config_info, update_sql_dir=None):
        self.update_sql_path = BuildUpdateSQL(self.database, self.data_source, self.assigned_study_id,
                                              self.assigned_replace_study_id).build(config_info, update_sql_dir)

    def run(self, is_public_network=True, config_info=None, ignore_error=False, latest_version=None,
            is_drop_database=True, incremental_sql_dir=None, update_sql_dir=None, is_kill_process=True):
        success = False
        try:
            if self.is_update or self.is_generate_update_sql_file:
                self.check_args()
            if is_kill_process is True:
                self._kill_db_process(update_sql_dir)
            total = self.count_total_table()
            if is_drop_database is True:
                self._drop_database()
            self._restore_database_and_count(total)
            if self.is_stop:
                return
            if self.is_update:
                try:
                    self._execute_procedures()
                    self._update_database(config_info, update_sql_dir)
                    self._drop_procedures()
                except Exception as e:
                    raise Exception(e)
            if self.is_generate_update_sql_file and self.update_sql_path is None:
                self.set_update_sql_path(config_info, update_sql_dir)
            if self.is_upgrade:
                ExecuteScript(self.app_db_route).execute_incremental_sql(
                    ignore_error, latest_version, incremental_sql_dir)
            success = True
        except Exception as e:
            self.exception = str(traceback.format_exc())
            raise Exception(e)
        finally:
            if self.is_stop is False:
                RedisBiz(self.app_db_route.get("host"), self.system, self.study_id, self.app_env).delete(
                    is_public_network)
                self.migration_rate = 100 if success else 99
                time.sleep(2)

    def _restore_database_and_count(self, total):
        global stop_threads
        stop_threads = False
        q = queue.Queue()
        t1 = threading.Thread(target=self._restore_database, args=(q,))
        t2 = threading.Thread(target=self.count_app_table, args=(total,))
        t1.start()
        t2.start()
        while True:
            if not t1.is_alive():
                stop_threads = True
                try:
                    exception = q.get_nowait()
                except queue.Empty:
                    self.migration_rate = 99
                    break
                else:
                    raise Exception(exception)
            if self.is_stop:
                break
            time.sleep(2)
        globals().pop("stop_threads")

    def count_total_table(self):
        total = BaseDb(self.app_db_route).get_table_count()
        cus_total = dict(edc=122, design=75, iwrs=46, ctms=152, etmf=22)
        return cus_total.get(self.system) if (total < cus_total.get(self.system, -1)) else total

    def count_app_table(self, total):
        table_counts = 0
        start = time.perf_counter()
        while table_counts < total:
            try:
                if self.is_stop:
                    break
                time.sleep(1)
                if BaseDb(self.app_db_route).get_table_count() == table_counts:
                    continue
                table_counts = BaseDb(self.app_db_route).get_table_count()
                table_counts = table_counts if table_counts else 1
                a = "*" * table_counts
                b = "." * (total - table_counts)
                c = (table_counts / total) * 100
                if 2 < c < 99:
                    self.migration_rate = round(c, 2)
                if c >= 100 or ("stop_threads" in globals() and stop_threads) or ("stop_threads" not in globals()):
                    break
                dur = time.perf_counter() - start
                print("\r{:^3.0f}%[{}->{}]{:.2f}s\n".format(c, a, b, dur), end="")
            except Exception as e:
                raise Exception(e)

    def check_args(self):
        study_id = self.assigned_study_id if self.assigned_replace_study_id is not None else self.study_id
        res = AdminDb(self.data_source).get_sponsor_id(study_id)
        if res is None:
            raise Exception("This study does not exist.")
        if self.sponsor_id != 0:
            res = AdminDb(self.data_source).get_company_id(self.sponsor_id)
            if res is None:
                raise Exception("This sponsor does not exist.")
        if self.app_env not in ["dev", "uat", "prod"]:
            raise Exception("Please check the system env.")

    def check_admin_data(self):
        has_role_check, has_site_check = False, False
        if self.system in ["edc", "iwrs"]:
            has_site_check = True
            if self.system == "edc":
                has_role_check = True
        return AdminDb(self.data_source).check_admin_data(self.study_id, self.app_env, has_site_check, has_role_check)

    def get_study_site_info(self, app):
        if app == App.edc:
            return EdcDb(self.app_db_route).get_study_site_info()
        elif app == App.iwrs:
            return IwrsDb(self.app_db_route).get_study_site_info()
        elif app == App.design:
            return DesignDb(self.app_db_route).get_study_info()
        else:
            return None, None

    def _execute_procedures(self):
        procedures_path = get_create_procedure_sql_path()
        return MysqlTask(**self.app_db_route).mysql_task(procedures_path)

    def _drop_procedures(self):
        procedures_path = get_drop_procedure_sql_path()
        return MysqlTask(**self.app_db_route).mysql_task(procedures_path)

    def stop(self):
        """
        清除数据库线程
        新建数据库
        :return:
        """
        self.is_stop = True
        self._kill_db_process()
        self._drop_database()
        print("Stop migration successfully.")

    def drop_all_views(self):
        return BaseDb(self.app_db_route).drop_all_views()

    def truncate_table(self, table_name):
        return BaseDb(self.app_db_route).truncate_table(table_name)

    def count_table(self, table_name):
        return BaseDb(self.app_db_route).count_table(table_name)

    def fetchall(self, sql, params=None):
        return BaseDb(self.app_db_route).fetchall(sql, params) or dict()

    def init_schema_history_and_latest_sql_version(self, latest_version_id):
        return ExecuteScript(self.app_db_route).init_schema_history_and_latest_sql_version(latest_version_id)

    def _kill_db_process(self, update_sql_dir=None):
        data_source = copy.deepcopy(self.app_db_route)
        data_source["db"] = None
        items = BaseDb(data_source).get_all_process_id(self.database)
        n = 1
        while items:
            if update_sql_dir is None:
                dir_path = build_sql_file_parent_path(self.app_db_route.get("host", "tmp"))
            else:
                dir_path = os.path.join(update_sql_dir, self.data_source.get("host", "tmp"))
            os.makedirs(dir_path, exist_ok=True)
            file_path = os.path.join(dir_path, f"kill_{self.database}_{time.time()}.sql")
            with open(file_path, "w", encoding="utf-8") as f:
                f.write("\n".join(items))
            try:
                print(f"The {n} time to clean up the database process.")
                MysqlTask(**data_source).mysql_task(file_path)
            except Exception as e:
                print(e)
            items = BaseDb(data_source).get_all_process_id(self.database)
            if os.path.exists(file_path):
                os.remove(file_path)
            if n > 10 and len(items) > 0:
                raise Exception("The database cleaning process has been carried out 10 times, and there are still "
                                "pending processes. Please contact the administrator for processing.")
            n += 1
