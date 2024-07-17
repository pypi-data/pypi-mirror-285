import logging
from io import BytesIO

import boto3
from botocore.config import Config
from taichu_storage import StorageInterface
import os

logger = logging.getLogger(__name__)


class StorageBoto3(StorageInterface):
    def __init__(self, cfgs=None):
        if cfgs is None:
            cfgs = {}
        ak = cfgs.get('ak')
        sk = cfgs.get('sk')
        endpoint_url = cfgs.get('endpoint_url')
        prefix = cfgs.get('bucket', '')
        minio_bucket = cfgs.get('minio_bucket')
        endpoint_url_external = cfgs.get('endpoint_url_external')
        if not endpoint_url and endpoint_url_external:
            endpoint_url = endpoint_url_external
        if prefix and not prefix.endswith('/'):
            prefix = prefix + '/'
        self._prefix = prefix
        self._bucket = minio_bucket if minio_bucket else 'alluxio'
        self._client = self.init_client(ak, sk, endpoint_url)
        if endpoint_url_external:
            self._client_external = self.init_client(ak, sk, endpoint_url_external)
        else:
            self._client_external = self._client

    def init_client(self, ak, sk, endpoint_url):
        client = boto3.client(
            's3',
            aws_access_key_id=ak,
            aws_secret_access_key=sk,
            use_ssl=True,
            region_name='default',
            endpoint_url=endpoint_url,
            config=Config(s3={"addressing_style": "path", "signature_version": 's3v4'},
                          connect_timeout=1, retries={'max_attempts': 1}))
        client.list_buckets()
        logger.info(f"Successfully connected to S3, endpoint_url: {endpoint_url}")
        return client

    def list_objects(self, key, delimiter=''):
        key = f'{self._prefix}{key}'
        result = []
        response = self._client.list_objects_v2(Bucket=self._bucket, Prefix=key, Delimiter=delimiter)
        if 'CommonPrefixes' in response:
            folders = []
            for item in response['CommonPrefixes']:
                folders.append({
                    'name': item['Prefix'].replace(self._prefix, '', 1),
                    'is_dir': True,
                    'size': 0,
                    'last_modified': None,
                })
            result.extend(folders)
        if 'Contents' in response:
            objects = []
            for item in response['Contents']:
                if item['Key'].endswith('/'):
                    continue
                objects.append({
                    'name': item['Key'].replace(self._prefix, '', 1),
                    'is_dir': False,
                    'size': item['Size'],
                    'last_modified': item['LastModified'].strftime("%Y-%m-%d %H:%M:%S"),
                })
            result.extend(objects)
        return result

    def get_object(self, key):
        key = f'{self._prefix}{key}'
        response = self._client.get_object(Bucket=self._bucket, Key=key)
        return BytesIO(response.get('Body').read())

    def put_object(self, key, content):
        key = f'{self._prefix}{key}'
        return self._client.put_object(Body=content, Bucket=self._bucket, Key=key)

    def upload_file(self, local_filename, key):
        key = f'{self._prefix}{key}'
        return self._client.upload_file(local_filename, self._bucket, key)

    def upload_dir(self, local_dir, key):
        local_dir = local_dir.rstrip('/')
        key = key.rstrip('/')
        for item in os.scandir(local_dir):
            remote_key = item.path.replace(local_dir, key)
            if item.is_file():
                self.upload_file(item.path, remote_key)
            elif item.is_dir():
                self.upload_dir(item.path, remote_key)

    def download_file(self, key, local_filename):
        key = f'{self._prefix}{key}'
        return self._client.download_file(self._bucket, key, local_filename)

    def download_dir(self, key, local_dir):
        key = f'{self._prefix}{key}'
        response = self._client.list_objects_v2(Bucket=self._bucket, Prefix=key)
        m = {}
        for obj in response.get('Contents', []):
            s3_key = obj['Key']
            local_file_path = f'{local_dir}{s3_key.replace(key, "")}'
            dirname = os.path.dirname(local_file_path)
            if not m.get(dirname, False):
                os.makedirs(dirname, exist_ok=True)
                m[dirname] = True
            if local_file_path.endswith('/'):
                continue
            self._client.download_file(self._bucket, s3_key, local_file_path)

    def copy_object(self, source_key, target_key):
        target_dir = os.path.dirname(target_key)
        self.create_dir(target_dir)
        source_key = f'{self._prefix}{source_key}'
        target_key = f'{self._prefix}{target_key}'
        return self._client.copy_object(Bucket=self._bucket, Key=target_key,
                                 CopySource={'Bucket': self._bucket, 'Key': source_key})

    def copy_dir(self, source_dir, dest_dir):
        source_dir = f'{self._prefix}{source_dir}'
        dest_dir = f'{self._prefix}{dest_dir}'
        objects = self._client.list_objects_v2(Bucket=self._bucket, Prefix=source_dir)
        if 'Contents' not in objects:
            logging.info("No files found in the source folder.")
            return
        m = {}
        for obj in objects['Contents']:
            if obj['Key'].endswith('/'):
                continue
            copy_source = {'Bucket': self._bucket, 'Key': obj['Key']}
            dest_key = obj['Key'].replace(source_dir, dest_dir, 1)
            dirname = os.path.dirname(dest_key)
            if not m.get(dirname):
                self._client.put_object(Bucket=self._bucket, Key=dirname + '/')
                m[dirname] = True
            self._client.copy_object(CopySource=copy_source, Bucket=self._bucket, Key=dest_key)
        return None

    def create_dir(self, dirname):
        key = f'{self._prefix}{dirname}'
        if not key.endswith('/'):
            key = key + '/'
        return self._client.put_object(Bucket=self._bucket, Key=key)

    def generate_signed_url(self, key, expiration=3600, use_external_host=True, content_type=None):
        key = f'{self._prefix}{key}'
        client = self._client
        if use_external_host:
            client = self._client_external
        params = {'Bucket': self._bucket, 'Key': key}
        if content_type:
            params['ResponseContentType'] = content_type
        url = client.generate_presigned_url(
            'get_object',
            Params=params,
            ExpiresIn=expiration,
        )
        return url

    def generate_upload_credentials(self, key, expiration=3600, use_external_host=True):
        key = f'{self._prefix}{key}'
        client = self._client
        if use_external_host:
            client = self._client_external
        response = client.generate_presigned_post(self._bucket, key, ExpiresIn=expiration)

        return response
