from typing import Literal
import boto3
from botocore.client import Config
from rov_db_access.config.settings import Settings

settings = Settings()


class S3Client:
    def __init__(self, bucket_name, bucket_region):
        self.bucket_name = bucket_name
        self.region = bucket_region
        self.access_key_id = settings.aws_key
        self.secret_access_key = settings.aws_secret

        self.s3 = boto3.client(
            "s3",
            aws_access_key_id=self.access_key_id,
            aws_secret_access_key=self.secret_access_key,
            config=Config(signature_version='s3v4', region_name=self.region)
        )

    def upload_file(self, file_path, key):
        self.s3.upload_file(file_path, self.bucket_name, key)

    def download_file(self, key, file_path):
        self.s3.download_file(self.bucket_name, key, file_path)

    def delete_file(self, key):
        self.s3.delete_object(Bucket=self.bucket_name, Key=key)

    def list_files(self):
        response = self.s3.list_objects_v2(Bucket=self.bucket_name)
        return [obj['Key'] for obj in response['Contents']]

    def get_file(self, key):
        response = self.s3.get_object(Bucket=self.bucket_name, Key=key)
        return response['Body'].read()

    def get_file_url(self, key):
        return f'https://{self.bucket_name}.s3.{self.region}.amazonaws.com/{key}'

    def put_file(self, key, data):
        self.s3.put_object(Bucket=self.bucket_name, Key=key, Body=data)

    def copy_file(self, src_key, dest_key):
        self.s3.copy_object(Bucket=self.bucket_name, CopySource=self.bucket_name + '/' + src_key, Key=dest_key)

    def get_presigned_url(self, key, action: Literal['get_object', 'put_object']):
        url = self.s3.generate_presigned_url(
            action,
            Params={'Bucket': self.bucket_name, 'Key': key},
            ExpiresIn=60
        )
        return url

    def check_file_exists(self, key):
        try:
            self.s3.head_object(Bucket=self.bucket_name, Key=key)
            return True
        except:
            return False

