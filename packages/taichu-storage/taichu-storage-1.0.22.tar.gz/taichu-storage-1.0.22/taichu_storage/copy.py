import logging
import os

from taichu_storage.obs_client import StorageObs

logger = logging.getLogger(__name__)


def copy(src: str, dst: str, retry_times=None):
    if src is None or len(src) == 0:
        raise Exception("src path required")
    if dst is None or len(dst) == 0:
        raise Exception("src path required")

    src = src.strip()
    dst = dst.strip()
    if src.startswith("obs://") and not dst.startswith("obs://"):
        download_from_obs(src, dst, retry_times=retry_times)
    elif not src.startswith("obs://") and dst.startswith("obs://"):
        upload_to_obs(src, dst, retry_times=retry_times)
    else:
        logger.info("Not supported yet")


def download_from_obs(src, dest, ak=None, sk=None, endpoint_url=None,
                      retry_times=None):
    src_bucket, src_key = parse_obs_path(src)
    client = StorageObs(cfgs={
        'bucket': src_bucket,
        'ak': ak,
        'sk': sk,
        'endpoint_url': endpoint_url})
    if src_key.endswith("/"):
        client.download_dir(src_key, dest, retry_times=retry_times)
    else:
        client.download_file(src_key, dest, retry_times=retry_times)


def upload_to_obs(src, dest, ak=None, sk=None, endpoint_url=None):
    dest_bucket, dest_key = parse_obs_path(dest)

    if not os.path.exists(src):
        raise Exception("src path {} does not exist".format(src))

    client = StorageObs(cfgs={
        'bucket': dest_bucket,
        'ak': ak,
        'sk': sk,
        'endpoint_url': endpoint_url})

    if os.path.isfile(src):
        client.upload_file(src, dest_key)
        return

    client.upload_dir(src, dest_key)


def parse_obs_path(obs_path):
    if obs_path.startswith("obs://"):
        obs_path = obs_path[6:]

    bucket = obs_path.split("/")[0]
    key = obs_path[len(bucket) + 1:]

    return bucket, key
