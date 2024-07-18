import json
import os
import uuid
from datetime import datetime

from minio import Minio
from minio.error import S3Error


def _generate_object_name(file_path):
    now = datetime.now()
    year, month, day = now.year, now.month, now.day
    file_name = os.path.basename(file_path)
    return "{}/{}/{}/{}/{}".format(year, month, day, uuid.uuid4(), file_name)


class MinioComponent:
    def __init__(self, endpoint, access_key, secret_key):
        self.endpoint = endpoint
        self.client = Minio(endpoint=endpoint,
                            access_key=access_key,
                            secret_key=secret_key,
                            secure=False)

    '''文件下载'''
    """
        Args:
            bucket_name (str): 桶名称.
            object_name (str): 桶中文件对象名称.
            file_path (str): 下载存储路径."""

    def download_file(self, bucket_name, object_name, file_path):

        try:
            self.client.fget_object(bucket_name, object_name, file_path)
        except S3Error as exc:
            print("Error occurred during file download", exc)

    '''文件上传'''
    """
        Args:
            bucket_name (str): 桶名称.
            file_path (str): 目标文件路径."""

    def upload_file_with_expire(self, bucket_name, file_path):
        object_name = _generate_object_name(file_path)
        try:
            self._create_bucket(bucket_name)
            self.client.fput_object(bucket_name, object_name, file_path)
            url = self.client.presigned_get_object(bucket_name, object_name)
            print("url:", url)
            return url
        except S3Error as exc:
            print(f"Error occurred during file upload: {exc}")
            return None

    def upload_file(self, bucket_name, file_path):
        object_name = _generate_object_name(file_path)
        try:
            self._create_bucket(bucket_name)
            self.client.fput_object(bucket_name, object_name, file_path)
            url = f"http://{self.endpoint}/{bucket_name}/{object_name}"
            print("url:", url)
            return url
        except S3Error as exc:
            print(f"Error occurred during file upload: {exc}")
            return None

    def _create_bucket(self, bucket_name):
        if not self.client.bucket_exists(bucket_name):
            self.client.make_bucket(bucket_name)
            # 设置桶的公共访问策略
            policy = {
                "Version": "2012-10-17",
                "Statement": [
                    {
                        "Effect": "Allow",
                        "Principal": {"AWS": "*"},
                        "Action": ["s3:GetObject"],
                        "Resource": [f"arn:aws:s3:::{bucket_name}/*"]
                    }
                ]
            }
            self.client.set_bucket_policy(bucket_name, json.dumps(policy))
