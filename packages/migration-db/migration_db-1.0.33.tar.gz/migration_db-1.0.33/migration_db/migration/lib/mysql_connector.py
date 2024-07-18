# !/usr/bin/python3
# -*- coding:utf-8 -*-
"""
@Author: xiaodong.li
@Time: 1/18/2024 3:28 PM
@Description: Description
@File: mysql_connector.py
"""
import os
import threading
from contextlib import contextmanager
from pathlib import Path

import mysql
from mysql.connector import errorcode
from mysql.connector.pooling import MySQLConnectionPool, PooledMySQLConnection
from slicing.constant import ListFileInfo
from slicing.info.file_info_list import FileInfoList


class RMySQLConnectionPool(MySQLConnectionPool):

    def __init__(self, **config):
        pool_size = config.get("pool_size", 3)
        self._semaphore = threading.Semaphore(pool_size)
        super().__init__(**config)

    def get_connection(self) -> PooledMySQLConnection:
        self._semaphore.acquire()
        return super().get_connection()

    def put_connection(self, cnx: PooledMySQLConnection):
        try:
            cnx.close()
        except mysql.connector.Error as err:
            if err.errno in (errorcode.CR_SERVER_LOST, -1):
                print(err.msg)
            else:
                raise Exception(err)
        except Exception as e:
            raise Exception(e)
        self._semaphore.release()

    def remove_connections(self):
        return super()._remove_connections()


class MysqlConnector:

    def __init__(self, host, port, password, user, db=None):
        self.size = 3
        self.connection_pool = RMySQLConnectionPool(
            pool_name="r_mysql_connector_pool",
            pool_size=self.size,
            host=host,
            database=db,
            user=user,
            password=password,
            port=port
        )
        self._lock = threading.Lock()

    def restore_from_slice_path(self, slice_path, is_restore_all_tables, tables):
        """
        1. 创建所有表
        2. 3个线程，按表维度进行还原
        :param slice_path: 拆分表的顶层目录
        :param is_restore_all_tables: 是否还原所有表
        :param tables: 需要还原的表
        :return:
        """
        file_list = FileInfoList(where=Path(slice_path))
        ac_tables = file_list.table(list_type=ListFileInfo.CREATE)
        if is_restore_all_tables is False:
            ex_tables = list(set(ac_tables) & set(tables))
        else:
            ex_tables = ac_tables
        # 执行sql文件
        for token in [ListFileInfo.CREATE, ListFileInfo.INSERT]:
            sql_paths = list()
            for table in ex_tables:
                # 还原部分表时，先删除表
                if is_restore_all_tables is False and token == ListFileInfo.CREATE:
                    drop_sqls = file_list.find(table, list_type=ListFileInfo.DROP)
                    self.thread_execute(
                        [os.path.join(slice_path, sql.sql_type, sql.name + ".sql") for sql in drop_sqls])
                sqls = file_list.find(table, list_type=token)
                sqls_len = len(sqls)
                if token == ListFileInfo.CREATE:
                    if sqls_len > 1:
                        raise Exception(f"表{table}存在多个创建语句。")
                    elif sqls_len == 0:
                        raise Exception(f"表{table}不存在创建语句。")
                if sqls_len > 0:
                    sql_paths.extend([os.path.join(slice_path, sql.sql_type, sql.name + ".sql") for sql in sqls])
            if len(sql_paths):
                self.threads_execute(sql_paths)
            print(f"{token} is end.")
        # 按顺序还原视图
        views = file_list.view(ListFileInfo.CREATE)
        sql_paths = list()
        for view in views:
            sqls = file_list.find(view, ListFileInfo.ALL)
            sqls = sorted(sqls, key=lambda file_info: file_info.no)
            if len(sqls) > 0:
                sql_paths.extend([os.path.join(slice_path, sql.sql_type, sql.name + ".sql") for sql in sqls])
        self.thread_execute(sql_paths)

    def threads_execute(self, sql_paths):
        threads = []
        for s in range(self.size):
            if len(sql_paths) > 0:
                t = threading.Thread(target=self.thread_execute,
                                     args=(sql_paths,),
                                     name="thread_execute")
                threads.append(t)
                t.start()
        for t in threads:
            t.join()

    def thread_execute(self, task_queue):
        while True:
            task = None
            with self._lock:
                if task_queue:
                    task = task_queue.pop(0)
            if not task:
                break
            self.execute_sql_file(task)

    def execute_sql_file(self, sql_path, foreign_key_checks=True):
        with open(sql_path, "rb") as rf:
            stmt = rf.read()
        with self.get_cursor() as cursor:
            if foreign_key_checks is True:
                cursor.execute("SET FOREIGN_KEY_CHECKS=FALSE;")
            cursor.execute(stmt)

    @contextmanager
    def get_cursor(self):
        cnx = None
        cursor = None
        is_exception = False
        try:
            cnx = self.connection_pool.get_connection()
            cursor = cnx.cursor()
            yield cursor
        except mysql.connector.Error as err:
            raise Exception(err.msg)
        except Exception as e:
            is_exception = True
            raise Exception(e)
        finally:
            if cursor is not None:
                cursor.close()
            if cnx is not None:
                if is_exception is False:
                    cnx.commit()
                self.connection_pool.put_connection(cnx)

    def __del__(self):
        self.connection_pool.remove_connections()
