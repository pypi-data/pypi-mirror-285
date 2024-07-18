"""
Author: xiaodong.li
Date: 2020-09-10 12:51:15
LastEditors: xiaodong.li
LastEditTime: 2020-09-23 15:43:30
Description: file content
"""

import redis
from common_utils.log import Logger


def connect_redis(db, host, port=6379, password="Admin123"):
    pool = redis.ConnectionPool(host=host, port=port, db=db, password=password, socket_connect_timeout=5)
    conn = redis.Redis(connection_pool=pool)
    try:
        conn.ping()
    except TimeoutError:
        raise Exception('redis connection timeout.')
    return conn


def delete_key(db, string, host, port=6379, password="Admin123"):
    if db not in list(range(6)):
        return
    conn = connect_redis(db, host, port, password)
    has_key = False
    index = 1
    for k in conn.keys():
        if f"{string}" in str(k):
            if index <= 10:
                Logger().info(k)
            conn.delete(k)
            has_key = True
            index += 1
    conn.close()
    if not has_key:
        Logger().info(f"DB({db}) Empty!")


def app_code_dict():
    return dict(design=3, edc=4, iwrs=5)


def delete_edc_design_key(study_id, host="200.200.101.97"):
    string = f"study:{study_id}"
    delete_key(3, string, host)
    delete_key(4, string, host)


def delete_portal_key(k, host="200.200.101.97"):
    delete_key(0, k, host)


def console_key(app, host, string):
    db = app_code_dict().get(app, None)
    if db not in list(range(6)):
        return
    conn = connect_redis(db, host)
    has_key = False
    for k in conn.keys():
        if f"{string}" in str(k):
            print(k)
            print(conn.get(k))
            # conn.delete(k)
            has_key = True
    if not has_key:
        Logger().info(f"DB({db}) Empty!")
    conn.close()


def delete_all_key(db, string, host, port=6379, password="Admin123"):
    if db not in list(range(6)):
        return
    conn = connect_redis(db, host, port, password)
    list_keys = conn.keys(f"*{string}*")
    if list_keys:
        Logger().info(list_keys[: 10 if len(list_keys) > 10 else len(list_keys)])
        delete_result = conn.delete(*list_keys)
        Logger().info(f"Delete {delete_result} redis keys.")
    else:
        Logger().info(f"DB({db}) Empty!")
