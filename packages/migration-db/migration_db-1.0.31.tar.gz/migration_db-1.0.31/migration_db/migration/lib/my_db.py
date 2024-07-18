"""
Created on Nov 27, 2019

@author: xiaodong.li
"""
import traceback

import pymysql
from common_utils.log import Logger
from pymysql import cursors


class MyDB:
    """
    define my database
    """

    def __init__(self, config):
        """
        initialization parameters
        :param config: object
        """
        self.connect_params = dict(host=config.host, port=config.port, user=config.user,
                                   password=config.password, db=config.db, charset='utf8mb4',
                                   cursorclass=cursors.DictCursor)
        self.env = f"{config.host} / {config.db}"
        self.conn = None
        self.cur = None
        self.connect()

    def connect(self):
        """
        : 获取连接对象和执行对象
        :return:
        """
        try:
            self.conn = pymysql.Connect(**self.connect_params)
            self.cur = self.conn.cursor()
            Logger().debug(f"Connect Database ({self.env}) successfully.")
        except Exception as e:
            traceback.print_exc()
            return Logger().error(f"Connect Database ({self.env}): Mysql Error{e}.")

    def fetchone(self, sql, params=None) -> dict or list:
        """
        : 根据sql和参数获取一行数据
        :param sql: sql语句
        :param params: sql语句对象的参数元祖，默认值为None
        :return: 查询的一行数据
        """
        data_one = None
        try:
            count = self.cur.execute(sql, params)
            Logger().debug(f"SQL>>>\n\t\t\t\t{self.cur._executed}")
            if count != 0:
                data_one = self.cur.fetchone()
            else:
                Logger().debug("The SQL query data is empty.")
        except Exception as ex:
            Logger().error(ex)
        finally:
            self.close()
        return data_one

    def fetchall(self, sql, params=None) -> list:
        """
        : 根据sql和参数获取一行数据
        :param sql: sql语句
        :param params: sql语句对象的参数列表，默认值为None
        :return: 查询的一行数据
        """
        data_all = None
        try:
            count = self.cur.execute(sql, params)
            Logger().debug(f"SQL>>>\n\t\t\t\t{self.cur._executed}")
            if count != 0:
                data_all = self.cur.fetchall()
            else:
                Logger().debug("The SQL query data is empty.")
        except Exception as ex:
            Logger().error(ex)
        finally:
            self.close()
        return data_all

    def execute(self, sql, params=None):
        """
        : 执行sql
        :param sql: sql语句
        :param params: sql语句对象的参数列表，默认值为None
        :return:
        """
        try:
            self.cur.execute(sql, params)
            Logger().debug(f"SQL>>>\n\t\t\t\t{self.cur._executed}")
        except Exception as ex:
            return Logger().error(ex)
        return self

    def commit(self):
        self.conn.commit()
        return self

    def _items(self, sql, params=None):
        """
        : 执行增删改
        :param sql: sql语句
        :param params: sql语句对象的参数列表，默认值为None
        :return: 受影响的行数
        """
        try:
            self.cur.execute(sql, params)
            self.conn.commit()
        except Exception as ex:
            Logger().error(ex)

    def update(self, sql, params=None):
        """
        : 执行修改
        :param sql: sql语句
        :param params: sql语句对象的参数列表，默认值为None
        :return: 受影响的行数
        """
        return self._items(sql, params)

    def insert(self, table_name, table_data):
        """
        : 执行新增
        :param table_name: 表名
        :param table_data: 数据字典
        :return: 受影响的行数
        """
        keys = ','.join(table_data.keys())
        values = ','.join(['%s'] * len(table_data))
        sql = 'INSERT INTO {table}({keys}) VALUES ({values});'.format(
            table=table_name, keys=keys, values=values)
        try:
            self._items(sql, params=tuple(table_data.values()))
            Logger().info("插入数据成功.")
        except:
            self.cur.rollback()
            self.close()
            Logger().error("插入数据失败.")

    def delete(self, table_name, table_data):
        """
        : 执行删除
        :param table_name: 表名
        :param table_data: 数据字典
        :return: 受影响的行数
        """
        params = ""
        for keys in table_data.keys():
            if keys == list(table_data.keys())[-1]:
                params = params + keys + ' = %s'
                break
            params = params + keys + " = %s and "
        sql = 'DELETE FROM {table} WHERE {params};'.format(table=table_name,
                                                           params=params)
        try:
            self._items(sql, params=tuple(table_data.values()))
            Logger().info(
                f"The data in the table ({table_name}) has been deleted."
            )
        finally:
            self.close()

    def close(self):
        """
        : 关闭执行工具和连接对象
        """
        try:
            if self.cur is not None:
                self.cur.close()
            if self.conn is not None:
                self.conn.close()
                Logger().debug("Database closed.")
        except Exception as e:
            return Logger().error("Mysql Error {0}".format(e))
