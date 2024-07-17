import logging
from abc import abstractmethod, ABC
from enum import Enum

logging.basicConfig(level=logging.INFO,  # 打印日志等级
                    format='%(asctime)s %(levelname)s %(filename)s:%(lineno)d - %(threadName)s : %(message)s',  # 日志内容
                    datefmt='[%Y-%m-%d %H:%M:%S]',  # 日期格式
                    # filename='./my.log',  # 日志存放位置
                    # filemode='w'
                    )


class Protocol(Enum):
    OBS = 1
    BOTO3 = 2


class StorageInterface(ABC):

    @abstractmethod
    def list_objects(self, key, delimiter=''):
        pass

    @abstractmethod
    def get_object(self, key):
        pass

    @abstractmethod
    def put_object(self, key, content):
        pass

    @abstractmethod
    def upload_file(self, local_filename, key):
        pass

    @abstractmethod
    def upload_dir(self, local_dir, key):
        pass

    @abstractmethod
    def download_file(self, key, local_filename):
        pass

    @abstractmethod
    def download_dir(self, key, local_dir):
        pass

    @abstractmethod
    def copy_object(self, source_key, target_key):
        pass

    @abstractmethod
    def copy_dir(self, source_dir, dest_dir):
        pass

    @abstractmethod
    def create_dir(self, dirname):
        pass

    @abstractmethod
    def generate_signed_url(self, key, expiration=3600, use_external_host=True, content_type=None):
        pass

    @abstractmethod
    def generate_upload_credentials(self, key, expiration=3600, use_external_host=True):
        pass


def create_storage(protocol: Protocol, cfgs=None):
    if cfgs is None:
        cfgs = {}
    if protocol == Protocol.OBS:
        from taichu_storage.obs_client import StorageObs
        return StorageObs(cfgs)
    if protocol == Protocol.BOTO3:
        from taichu_storage.boto3_client import StorageBoto3
        return StorageBoto3(cfgs)
    return None
