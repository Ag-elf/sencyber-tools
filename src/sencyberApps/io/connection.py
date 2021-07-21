# -*- coding: utf-8 -*-
# @Time     : 2021/6/1 11:30
# @Author   : Shigure_Hotaru
# @Email    : minjie96@sencyber.cn
# @File     : connection.py
# @Version  : Python 3.8.5 +
import json
import oss2

from cassandra.cluster import Cluster, ResultSet
from cassandra.auth import PlainTextAuthProvider

from .geo import GeoPoint


class CassandraLoader:
    def __init__(self, secret_path="./secret/"):
        file_path = secret_path + '__secret_connection.json'
        a = jsonLoader(file_path)
        # print(a)

        ips = a['ip']
        usrName = a['username']
        pwd = a['password']

        self.node_ips = ips
        self.auth_provider = PlainTextAuthProvider(username=usrName, password=pwd)

        self.cluster = Cluster(self.node_ips, auth_provider=self.auth_provider)

        self.cluster.register_user_type('bohai_device_trip', 'geo_point', GeoPoint)
        self.cluster.register_user_type('sencyber_device_trip', 'geo_point', GeoPoint)

        print("Cassandra Server Connection Establishing...")
        self.session = self.cluster.connect()

    def execute(self, sql, data=()) -> ResultSet:
        if len(data) == 0:
            resultSet = self.session.execute(sql)
        else:
            resultSet = self.session.execute(sql, data)
        return resultSet

    def close(self):
        self.cluster.shutdown()
        print("Connection is shutting down...")
        return self.cluster.is_shutdown


class Oss2Connector:
    def __init__(self, secret_path="../secret/"):

        file_path = secret_path + '__secret_aliyun_info.json'
        a = jsonLoader(file_path)

        AccessKeyId = a['AccessKeyId']
        AccessKeySecret = a['AccessKeySecret']
        BucketName = a['BucketName']
        EndPoint = a['EndPoint']

        # access_key_id = os.getenv('OSS_TEST_ACCESS_KEY_ID', AccessKeyId)
        # access_key_secret = os.getenv('OSS_TEST_ACCESS_KEY_SECRET', AccessKeySecret)
        # bucket_name = os.getenv('OSS_TEST_BUCKET', BucketName)
        # endpoint = os.getenv('OSS_TEST_ENDPOINT', EndPoint)

        access_key_id = AccessKeyId
        access_key_secret = AccessKeySecret
        bucket_name = BucketName
        endpoint = EndPoint

        self.bucket = oss2.Bucket(oss2.Auth(access_key_id, access_key_secret), endpoint, bucket_name)

    def save(self, content: bytes, path: str):
        self.bucket.put_object(path, content)

    def exists(self, path: str) -> bool:
        try:
            self.bucket.get_object(path)
        except oss2.exceptions.NoSuchKey as e:
            return False

        return True


def jsonLoader(path: str):
    with open(path, 'r') as f:
        a = json.load(f)

    return a

