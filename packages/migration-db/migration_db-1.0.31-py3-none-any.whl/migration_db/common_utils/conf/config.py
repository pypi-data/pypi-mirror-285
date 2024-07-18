#!/usr/bin/python3
# -*- coding:utf-8 -*-
"""
@author: xiaodong.li
@time: 2/23/2023 9:56 PM
@desc:
"""


class Config(object):

    def __init__(self, host=None, user_name="root", password="Admin123", port=3306, database=None):
        self.__host = host
        self.__user_name = user_name
        self.__password = password
        self.__port = int(port)
        self.__database = database

    @property
    def host(self):
        return self.__host

    @host.setter
    def host(self, host):
        self.__host = host

    @property
    def user_name(self):
        return self.__user_name

    @user_name.setter
    def user_name(self, user_name):
        self.__user_name = user_name

    @property
    def password(self):
        return self.__password

    @password.setter
    def password(self, password):
        self.__password = password

    @property
    def port(self):
        return self.__port

    @port.setter
    def port(self, port):
        self.__port = int(port)

    @property
    def database(self):
        return self.__database

    @database.setter
    def database(self, database):
        self.__database = database
