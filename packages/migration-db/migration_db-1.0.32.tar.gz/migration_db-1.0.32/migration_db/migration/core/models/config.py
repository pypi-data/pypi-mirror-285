#!/usr/bin/python3
# -*- coding:utf-8 -*-
"""
@author: xiaodong.li
@time: 11/3/2020 9:56 PM
@desc:
"""


class Config(object):

    def __init__(self, host="200.200.101.108", user="root", password="Admin123", port=3306, db=None):
        self.__host = host
        self.__user = user
        self.__password = password
        self.__port = int(port)
        self.__db = db

    @property
    def host(self):
        return self.__host

    @host.setter
    def host(self, host):
        self.__host = host

    @property
    def user(self):
        return self.__user

    @user.setter
    def user(self, user):
        self.__user = user

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
    def db(self):
        return self.__db

    @db.setter
    def db(self, db):
        self.__db = db
