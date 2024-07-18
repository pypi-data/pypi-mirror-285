# !/usr/bin/python3
# -*- coding:utf-8 -*-
"""
@Author: xiaodong.li
@Time: 5/6/2024 9:54 AM
@Description: Description
@File: handle_archive_file.py
"""
import gzip
import os
import re
import time
import zipfile

from common_utils.calc_time import calc_func_time
from migration.lib.synchronized import synchronized

RM_SQL_STATE_PATTERN = r"^SET @@GLOBAL\.GTID_PURGED=.*?;|^CREATE DATABASE.*?;|^USE .*?;|.*?@@SESSION\.SQL_LOG_BIN.*?;"


def handle_archive(temp: str, filename: str, is_decompress_file=True, is_filter=True):
    temp_f_path = rename_archive(temp, filename)
    if is_decompress_file is False:
        return temp_f_path
    archive_f_path: str = os.path.join(temp, filename)
    if filename.endswith(".zip"):
        z_file = zipfile.ZipFile(archive_f_path)
        zip_list = z_file.namelist()
        if len(zip_list) != 1:
            raise Exception(f"Zip文件中包含{len(zip_list)}个文件。")
        for z in zip_list:
            if not z.endswith(".sql"):
                raise Exception(f"Zip文件中不包含sql文件。")
            z_file.extract(z, temp)
        z_file.close()
        if is_filter:
            tem_f_bak_path = temp_f_path + ".bak"
            os.rename(temp_f_path, tem_f_bak_path)
            with open(tem_f_bak_path, "rb") as f_bak:
                save_file(temp_f_path, f_bak, False)
    elif filename.endswith(".gz"):
        g_file = gzip.GzipFile(archive_f_path)
        save_file(temp_f_path, g_file, False)
    return temp_f_path


def handle_sql_file(temp: str, filename: str):
    temp_f_path = rename_archive(temp, filename)
    tem_f_bak_path = temp_f_path + ".bak"
    os.rename(temp_f_path, tem_f_bak_path)
    with open(tem_f_bak_path, "rb") as f_bak:
        save_file(temp_f_path, f_bak, False)
    return temp_f_path


@synchronized
@calc_func_time
def save_file(temp_f_path, f, is_archive):
    t1 = time.time()
    with open(temp_f_path, "wb") as file:
        try:
            while True:
                line = f.readline()
                if not is_archive:
                    try:
                        if len(line) > 0:
                            # 根据需要匹配的要求，截取一段SQL进行匹配可以满足需求
                            str_line = line[0: len(line) > 200 and 200 or len(line)].decode("utf-8").replace("\n", "")
                            if re.match(RM_SQL_STATE_PATTERN, str_line):
                                continue
                    except Exception as e:
                        print(e)
                file.write(line)
                if not line:
                    break
            print(f"循环lines耗时：{time.time() - t1}")
        except (BaseException, EOFError) as e:
            raise Exception(e)
        finally:
            f.close()


def rename_archive(temp: str, filename: str) -> str:
    temp_f_path: str = os.path.join(temp, filename)
    if filename.endswith(".zip"):
        temp_f_path = temp_f_path.replace(".zip", ".sql")
    elif filename.endswith(".gz"):
        match_obj = re.match(r".*?(\.sql.*?\.gz)", filename)
        if match_obj:
            match_str = match_obj.group(1)
            temp_f_path = temp_f_path.replace(match_str, ".sql")
        else:
            temp_f_path = temp_f_path.replace(".gz", "")
    return temp_f_path
