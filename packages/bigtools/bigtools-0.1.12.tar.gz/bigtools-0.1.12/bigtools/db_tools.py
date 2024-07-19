# -*- coding: UTF-8 -*-
# @Time : 2023/9/27 16:28 
# @Author : 刘洪波
from pymongo import MongoClient
from pytz import timezone
from minio.error import S3Error
from minio import Minio


def mongo_client(host: str, port, user: str = None, password: str = None,
                 tz_aware: bool = False, tzinfo: str = 'Asia/Shanghai'):
    uri = f"mongodb://{host}:{port}"
    if user and password:
        uri = f"mongodb://{user}:{password}@{host}:{port}"
    elif user:
        raise ValueError('Please check user and password')
    elif password:
        raise ValueError('Please check user and password')
    if tz_aware:
        return MongoClient(uri, tz_aware=tz_aware, tzinfo=timezone(tzinfo))
    return MongoClient(uri)


class MinioOperate(object):
    def __init__(self, minio_clinet: Minio):
        self.clinet = minio_clinet

    def create_bucket(self, bucket_name: str):
        """
        创建桶
        注：创建桶命名限制：小写字母，句点，连字符和数字是唯一允许使用的字符（使用大写字母、下划线等命名会报错），长度至少应为3个字符
        """
        try:
            # bucket_exists：检查桶是否存在
            if self.clinet.bucket_exists(bucket_name=bucket_name):
                print("该存储桶已经存在")
            else:
                self.clinet.make_bucket(bucket_name)
                print("存储桶创建成功")
            return True
        except S3Error as e:
            print(e)
        return False

    def get_bucket_list(self):
        buckets_list = []
        try:
            buckets = self.clinet.list_buckets()
            buckets_list = [{'name': bucket.name, 'creation_date': bucket.creation_date} for bucket in buckets]
            print(buckets_list)
        except S3Error as e:
            print(e)
        return buckets_list
