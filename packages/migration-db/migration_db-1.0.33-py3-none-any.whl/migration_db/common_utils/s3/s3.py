# !/usr/bin/python3
# -*- coding:utf-8 -*-
"""
@Author: xiaodong.li
@Time: 4/29/2024 3:32 PM
@Description: Description
@File: s3.py
"""
from enum import unique, Enum

import boto3
from boto3.s3.transfer import TransferConfig


@unique
class ObjectType(Enum):

    def __init__(self, code, description):
        self.code = code
        self.description = description

    FILE = (10, "File")
    FOLDER = (20, "Folder")
    BUCKET = (30, "Bucket")


def size2biz(size_in_bytes):
    size_in_bytes = float(size_in_bytes)
    kilo_bytes = size_in_bytes / 1024
    mega_bytes = kilo_bytes / 1024
    giga_bytes = mega_bytes / 1024
    if giga_bytes >= 1:
        return "{:.2f} GB".format(giga_bytes)
    elif mega_bytes >= 1:
        return "{:.2f} MB".format(mega_bytes)
    elif kilo_bytes >= 1:
        return "{:.2f} KB".format(kilo_bytes)
    else:
        return "{:.2f} bytes".format(size_in_bytes)


class ObjectDto(object):

    def __init__(self, object_type=None, name=None, key=None, size=str(), last_modified=str(), storage_class=str(),
                 index=None, size_str=str()):
        self.object_type = object_type
        self.name = name
        self.key = key
        self.size = size
        self.last_modified = last_modified
        self.storage_class = storage_class
        self.index = index
        self.size_str = size_str


def get_all_buckets(s3):
    items = sorted([ObjectDto(name=bucket["Name"]) for bucket in s3.list_buckets()['Buckets']],
                   key=lambda x: str.lower(x.name))
    for index, item in enumerate(items):
        item.index = index
    return items


def init_client():
    return boto3.client('s3')


def init_resource():
    return boto3.resource('s3')


def get_file(s3, bucket, filename):
    return s3.get_object(Bucket=bucket, Key=filename)


def have_bucket(s3, bucket):
    buckets = get_all_buckets(s3)
    return bucket in buckets and True or False


def get_top_level_common_prefixes(s3, bucket, prefix=None):
    """
    :param s3:
    :param bucket:
    :param prefix:
    :return:
    """
    paginator = s3.get_paginator('list_objects')
    result = paginator.paginate(Bucket=bucket, Delimiter='/', Prefix=prefix)
    common_prefixes = result.search('CommonPrefixes')
    common_prefixes_result = list()
    contents_result = list()
    for common_prefix in common_prefixes:
        if common_prefix is not None:
            folder_path = common_prefix.get('Prefix')
            folder_name = folder_path.replace(prefix, "")
            common_prefixes_result.append(ObjectDto(ObjectType.FOLDER, folder_name))
    contents = result.search('Contents')
    for content in contents:
        if content is not None:
            size = content.get("Size")
            if size > 0:
                key = content.get("Key")
                last_modified = content.get("LastModified")
                storage_class = content.get("StorageClass")
                if prefix.endswith("/"):
                    replaced_str = prefix
                elif "/" in prefix:
                    tmp = prefix.split("/")
                    tmp.pop()
                    tmp.append("")
                    replaced_str = "/".join(tmp)
                else:
                    replaced_str = str()
                file_name = key.replace(replaced_str, "")
                contents_result.append(
                    ObjectDto(ObjectType.FILE, file_name, key, size, last_modified, storage_class,
                              size_str=size2biz(size)))
    common_prefixes_result = sorted(common_prefixes_result, key=lambda x: str.lower(x.name), reverse=True)
    contents_result = sorted(contents_result, key=lambda x: x.last_modified, reverse=True)
    common_prefixes_result.extend(contents_result)
    for index, item in enumerate(common_prefixes_result):
        item.index = index
    return common_prefixes_result


def download(s3, bucket, key, local_file_path):
    return s3.Bucket(bucket).download_file(key, local_file_path,
                                           Config=TransferConfig(multipart_threshold=50 * 1024 * 1024,
                                                                 multipart_chunksize=50 * 1024 * 1024,
                                                                 io_chunksize=50 * 1024 * 1024))


# biz
def get_bucket(s3, bucket_id):
    buckets = get_all_buckets(s3)
    bucket = get_object_name(buckets, int(bucket_id))
    return bucket


def get_file_obj(s3, bucket, prefix_path):
    """
    get file object
    :param s3: s3 instance
    :param bucket: bucket name
    :param prefix_path: file path, 15/2/3
    :return: ObjectDto or None
    """
    details = get_obj_dto(s3, bucket, prefix_path)
    if len(details) == 1:
        return details[0]
    return None


def get_object_index(items, name):
    for item in items:
        if item.name == name:
            return item.index
    return 0


def get_object_name(items, index):
    for item in items:
        if item.index == index:
            return item.name
    return None


def get_obj_dto(s3, bucket, prefix_path):
    """
    get file object
    :param s3: s3 instance
    :param bucket: bucket name
    :param prefix_path: file path, 15/2/3
    :return: ObjectDto or None
    """
    prefix = str()
    details = get_top_level_common_prefixes(s3, bucket, prefix)
    if prefix_path is not None:
        prefix_path_list = prefix_path.split("/")
        tmp_prefix_path_list = [i for i in prefix_path_list if i != '']
        for index, i in enumerate(tmp_prefix_path_list):
            tmp_prefix = get_object_name(details, int(i))
            prefix += tmp_prefix
            details = get_top_level_common_prefixes(s3, bucket, prefix)
    return details


def upload(s3, file_path, bucket_name, key, is_local=False):
    if is_local is True:
        return s3.upload_file(file_path, bucket_name, key)
    s3.put_object(
        Bucket=bucket_name,
        Key=key,
        Body=file_path
    )


def get_file_size(s3, bucket_name, key):
    response = s3.head_object(Bucket=bucket_name, Key=key)
    return response['ContentLength']


def build_file_dtos(s3, bucket_name, keys):
    file_dtos = list()
    for key in keys:
        file_dto = ObjectDto()
        file_dto.size = get_file_size(s3, bucket_name, key)
        file_dto.name = key.split("/")[-1]
        file_dto.key = key
        file_dtos.append(file_dto)
    return file_dtos
