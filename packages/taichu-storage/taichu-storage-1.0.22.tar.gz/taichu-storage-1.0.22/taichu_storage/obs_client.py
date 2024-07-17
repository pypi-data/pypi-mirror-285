import logging
import math
import os.path
import threading
import time
from datetime import datetime
from taichu_storage import StorageInterface
from obs import ObsClient, PutObjectHeader
from obs import CompleteMultipartUploadRequest, CompletePart
import mimetypes
from io import BytesIO

logger = logging.getLogger(__name__)

local_data = threading.local()


def download_progress_callback(transferred_amount, total_amount, total_seconds):
    pre_total_seconds = 0.0
    try:
        pre_total_seconds = local_data.pre_total_seconds
    except:
        pass
    rate = round(transferred_amount * 100.0 / total_amount, 1)
    speed = int(transferred_amount * 1.0 / total_seconds / 1024)
    if total_seconds - pre_total_seconds >= 1:
        logger.info(f"正在下载中，进度：{rate}%，平均速率：{speed} (KB/S)，共耗时：{round(total_seconds, 1)} 秒")
        local_data.pre_total_seconds = total_seconds


class StorageObs(StorageInterface):

    def __init__(self, cfgs=None):
        if cfgs is None:
            cfgs = {'bucket': 'publish-data'}

        self._bucket = cfgs.get('bucket')
        obs_ak = cfgs.get('ak')
        obs_sk = cfgs.get('sk')
        obs_server = cfgs.get('endpoint_url')
        if obs_ak is None:
            obs_ak = os.environ.get('S3_AK')
        if obs_ak is None:
            obs_ak = os.environ.get('HW_OBS_AK')
        if obs_ak is None or len(obs_ak) == 0:
            raise Exception('obs ak is required')

        if obs_sk is None:
            obs_sk = os.environ.get('S3_SK')
        if obs_sk is None:
            obs_sk = os.environ.get('HW_OBS_SK')
        if obs_sk is None or len(obs_sk) == 0:
            raise Exception('obs sk is required')

        if obs_server is None:
            obs_server = os.environ.get('S3_ENDPOINT')
        if obs_server is None:
            obs_server = os.environ.get('HW_OBS_SERVER')
        if obs_server is None or len(obs_server) == 0:
            raise Exception('obs endpoint url is required')
        self._client = ObsClient(
            access_key_id=obs_ak,
            secret_access_key=obs_sk,
            server=obs_server
        )
        resp = self._client.headBucket(bucketName=self._bucket)
        if resp.status == 403:
            raise Exception(f'Connect failed, errorCode:{resp.errorCode}, errorMessage: {resp.errorMessage}')
        if resp.status == 404:
            raise Exception(f'Bucket {self._bucket} does not exist')
        logger.info("Successfully connected!")

    def list_objects(self, key, delimiter='', skip_empty_file=True):
        max_num = 1000
        mark = None
        result = []
        while True:
            resp = self._client.listObjects(bucketName=self._bucket, prefix=key, marker=mark,
                                            max_keys=max_num, delimiter=delimiter)
            if resp.status < 300:
                folders = []
                for folder in resp.body.commonPrefixs:
                    folders.append({
                        'name': folder.Prefix,
                        'is_dir': True,
                        'size': 0,
                        'last_modified': None,
                    })
                result.extend(folders)
                objects = []
                for content in resp.body.contents:
                    if skip_empty_file and content.key.endswith('/'):
                        continue
                    objects.append({
                        'name': content.key,
                        'is_dir': False,
                        'size': content.size,
                        'last_modified': datetime.strptime(content.lastModified, "%Y/%m/%d %H:%M:%S").strftime(
                            "%Y-%m-%d %H:%M:%S"),
                    })
                result.extend(objects)
                if resp.body.is_truncated is True:
                    mark = resp.body.next_marker
                else:
                    break
            else:
                logging.error(f'list_objects error,error_code:{resp.status}, message:{resp.errorMessage}')
                break

        return result

    def get_object(self, key):
        response = self._client.getObject(self._bucket, key, loadStreamInMemory=True)
        if response.status < 300:
            return BytesIO(response.body.buffer)
        return BytesIO()

    def put_object(self, key, content):
        return self._client.putContent(self._bucket, key, content=content)

    def upload_file(self, local_filename, key):
        headers = PutObjectHeader()
        content_type = 'text/plain'
        mime_type = mimetypes.guess_type(key)[0]
        if mime_type == 'text/plain':
            mime_type = 'text/plain;charset=utf-8'
        if mime_type:
            content_type = mime_type
        headers.contentType = content_type

        file_size = os.path.getsize(local_filename)
        if file_size > 2 * 1024 * 1024 * 1024:
            logger.info(f"file size {file_size} > 2G, use multipart upload")
            return self.multipart_upload(key, local_filename, content_type)

        return self._client.putFile(self._bucket, key, local_filename, metadata={}, headers=headers)

    def upload_dir(self, local_dir, key):
        local_dir = local_dir.rstrip('/')
        key = key.rstrip('/')
        return self.upload_file(local_dir, key)

    def download_file(self, key, local_filename, retry_times=3):
        logger.info(f"downloading {key} to {local_filename}")
        if retry_times is None or retry_times <= 0:
            retry_times = 1

        if local_filename.endswith('/'):
            os.makedirs(local_filename, exist_ok=True)
            local_filename = os.path.join(local_filename, key.split('/')[-1])

        for i in range(retry_times):
            resp = self._client.getObject(self._bucket, key, downloadPath=local_filename,
                                          progressCallback=download_progress_callback)
            if resp.status < 300:
                break

            logger.error(
                f'retry {i} times,key:{key},local_filename:{local_filename}， errorCode:{resp.errorCode}, errorMessage:{resp.errorMessage}')
            time.sleep(1)

    def download_dir(self, key, local_dir, retry_times=None):
        if local_dir.endswith('/'):
            local_dir = local_dir[:-1]
        objects = self.list_objects(key, skip_empty_file=False)
        for o in objects:
            local_filename = os.path.join(local_dir, o['name'].replace(key, ''))
            if o['is_dir']:
                continue
            if o['name'].endswith('/'):
                os.makedirs(local_filename, exist_ok=True)
                continue

            self.download_file(o['name'], local_filename, retry_times=retry_times)

    def copy_object(self, source_key, dest_key):
        resp = self._client.copyObject(self._bucket, source_key, self._bucket, dest_key)
        if not resp.status < 300:
            logging.error(f'copy_object error,error_code:{resp.errorCode}, message:{resp.errorMessage}')

    def copy_dir(self, source_path, dest_path):
        if not dest_path.endswith('/'):
            dest_path = dest_path + '/'
        objects = self.list_objects(source_path)
        for o in objects:
            source_key = o['name']
            dest_key = source_key.replace(source_path, dest_path)
            self.copy_object(source_key, dest_key)

    def create_dir(self, key):
        if not key.endswith('/'):
            key = key + '/'
        return self.put_object(None, key)

    def generate_signed_url(self, key, expiration=3600, use_external_host=True, content_type=None):
        rps = self._client.createSignedUrl("GET", self._bucket, key, expires=expiration)
        return rps.signedUrl

    def generate_upload_credentials(self, key, expiration=3600, use_external_host=True):
        content_type = 'text/plain'
        mime_type = mimetypes.guess_type(key)[0]
        if mime_type == 'text/plain':
            mime_type = 'text/plain;charset=utf-8'
        if mime_type:
            content_type = mime_type
        response = self._client.createSignedUrl("PUT", self._bucket, key,
                                                expires=expiration, headers={'Content-Type': content_type})
        return response

    def multipart_upload(self, key, file_path, content_type):
        is_file = True
        file_size = os.path.getsize(file_path)
        max_part_size = 1024 * 1024 * 500

        resp = self._client.initiateMultipartUpload(self._bucket, key, contentType=content_type)
        if resp.status >= 300:
            raise Exception(
                f"Failed to initiate multipart upload, requestId : {resp.requestId}, errorCode: {resp.errorCode}, errorMessage: {resp.errorMessage}")

        upload_id = resp.body.uploadId

        part_number = 1
        etag_list = []
        for i in range(0, file_size, max_part_size):
            part_size = max_part_size
            if file_size - i < max_part_size:
                part_size = file_size - i

            logger.info(f"正在上传第{part_number}个分片，大小：{part_size}字节")
            resp2 = self._client.uploadPart(self._bucket, key, part_number, upload_id, file_path, is_file, part_size,
                                            offset=i, progressCallback=None)
            if resp2.status >= 300:
                raise Exception(f"Failed to upload part, requestId : {resp2.requestId}, errorCode: {resp2.errorCode}, "
                                f"errorMessage: {resp2.errorMessage}")

            etag_list.append({'part_num': part_number, 'etag': resp2.body.etag})
            part_number += 1

        parts = []
        for item in etag_list:
            parts.append(CompletePart(partNum=item.get('part_num'), etag=item.get('etag')))

        completeMultipartUploadRequest = CompleteMultipartUploadRequest(parts=parts)
        resp3 = self._client.completeMultipartUpload(self._bucket, key, upload_id, completeMultipartUploadRequest)
        if resp3.status >= 300:
            raise Exception(
                f"Failed to complete multipart upload, requestId : {resp3.requestId}, errorCode: {resp3.errorCode}, "
                f"errorMessage: {resp3.errorMessage}")
