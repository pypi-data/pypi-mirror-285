import hashlib
import os
import time
from datetime import datetime
from pathlib import Path
from typing import BinaryIO, List, Optional, Union

import boto3
import requests
#from tqdm import tqdm

from dataset import Dataset, DatasetFile, UploadInfo

HEYWHALE_SITE = os.getenv("HEYWHALE_HOST", "https://www.heywhale.com")
HEYWHALE_DS_BUCKET = os.getenv("HEYWHALE_DS_BUCKET", "kesci")


def parse_datetime(date_string: str) -> datetime:
    """
    Parse a datetime string into a datetime object.

    :param date_string: The datetime string to parse.
    :return: A datetime object.
    """
    return datetime.strptime(date_string, "%Y-%m-%dT%H:%M:%S.%fZ")


def get_dataset(dataset_id: str, token: Optional[str] = None) -> Dataset:
    """
    Fetches dataset details from Heywhale.

    :param dataset_id: The ID of the dataset to fetch.
    :param token: The token for authentication. If not provided, the function will use the 'MW_TOKEN' environment variable.
    :return: A Dataset object with the dataset details.
    :raises ValueError: If no token is provided and the 'MW_TOKEN' environment variable is not set.
    """
    if token is None:
        token = os.getenv("MW_TOKEN")
        if not token:
            raise ValueError(
                "No token provided and 'MW_TOKEN' environment variable is not set."
            )

    url = f"{HEYWHALE_SITE}/api/datasets/{dataset_id}"
    headers = {
        "x-kesci-token": token,
        "x-kesci-resource": dataset_id,
    }

    response = requests.get(url, headers=headers, timeout=10)
    # pprint.pp(response.json().get("Files"))
    if response.status_code == 200:
        dataset_files = [
            DatasetFile(file.get("_id"), file.get("Token"), file.get("Size"))
            for file in response.json().get("Files")
        ]
        # pprint.pp(response.json())
        return Dataset(
            _id=response.json().get("_id"),
            title=response.json().get("Title"),
            short_description=response.json().get("ShortDescription"),
            folder_name=response.json().get("FolderName"),
            files=dataset_files,
            created_at=parse_datetime(response.json().get("CreateDate")),
            updated_at=parse_datetime(response.json().get("UpdateDate")),
        )
    else:
        response.raise_for_status()


def _update_dataset(id: str, files: List[DatasetFile], token: Optional[str] = None):
    if token is None:
        token = os.getenv("MW_TOKEN")
        if not token:
            raise ValueError(
                "No token provided and 'MW_TOKEN' environment variable is not set."
            )
    url = f"{HEYWHALE_SITE}/api/datasets/{id}/files"
    headers = {"x-kesci-token": token, "x-kesci-resource": id}
    # pprint.pp({
    #         "Files": [file.key for file in files],
    #     })
    response = requests.put(
        url,
        {
            "Files": [file.key for file in files],
        },
        headers=headers,
        timeout=10,
    )
    if response.status_code == 200:
        # print(response.text)
        return
    else:
        # print("bad request")
        print(response.text)
        response.raise_for_status()


def _get_update_token(token: Optional[str] = None) -> UploadInfo:
    if token is None:
        token = os.getenv("MW_TOKEN")
        if not token:
            raise ValueError(
                "No token provided and 'MW_TOKEN' environment variable is not set."
            )
    url = f"{HEYWHALE_SITE}/api/dataset-upload-token"
    headers = {"x-kesci-token": token}
    response = requests.get(url, headers=headers, timeout=10)
    if response.status_code == 200:
        # init upload token
        return UploadInfo(
            endpoint=response.json().get("endpoint"),
            ak=response.json().get("accessKeyId"),
            sk=response.json().get("secretAccessKey"),
            token=response.json().get("sessionToken"),
            bucket=response.json().get("bucket"),
            # path=response.json().get("path"),
            prefix_to_save=response.json().get("prefixToSave"),
            region=response.json().get("region"),
        )
    else:
        response.raise_for_status()


def generate_timestamped_string(revision: int) -> str:
    # Get the current timestamp in milliseconds
    timestamp = int(time.time() * 1000)
    # Create the desired string format
    result = f"{timestamp}_{revision}"
    return result


def upload_file(
    path_or_fileobj: Union[str, Path, bytes, BinaryIO],
    path_in_dataset: str,
    id: str,
    token: Optional[str] = None,
):
    if token is None:
        token = os.getenv("MW_TOKEN")
        if not token:
            raise ValueError(
                "No token provided and 'MW_TOKEN' environment variable is not set."
            )
    # Get update info
    upload_info = _get_update_token(token)
    # pprint.pp(upload_info)

    # Initialize a session using credentials
    session = boto3.Session(
        aws_access_key_id=upload_info.ak,
        aws_secret_access_key=upload_info.sk,
        aws_session_token=upload_info.token,
        region_name=upload_info.region,
    )

    # Initialize an S3 client
    s3 = session.client("s3", endpoint_url=upload_info.endpoint)

    # TODO: reivison and timestamp
    # Specify the bucket name and the object key
    bucket_name = upload_info.bucket
    object_key = os.path.join(
        upload_info.prefix_to_save, generate_timestamped_string(1), path_in_dataset
    )
    try:
        if isinstance(path_or_fileobj, (str, Path)):
            # Upload a file
            with open(path_or_fileobj, "rb") as file:
                s3.put_object(Bucket=bucket_name, Key=object_key, Body=file)
        else:
            # Upload a binary stream
            s3.put_object(Bucket=bucket_name, Key=object_key, Body=path_or_fileobj)
    except Exception as e:
        print(f"Error getting object '{object_key}' from bucket '{bucket_name}': {e}")

    dataset_files = get_dataset(id, token).files
    dataset_files.append(DatasetFile("", object_key, 0))
    # pprint.pp(dataset_files)
    _update_dataset(id, dataset_files, token)


# 初始化cache目录
# ~/.mw_cache/
#            /blobs/
#            /datasets/dataset-a/
#                               /refs/main 内容是2就代表main分支指向了第二个snapshot
#                               /snapshots/
#                                         /1/
#                                           a.txt -> ~/.mw_cache/blobs/xxxx
#                                         /2
#                                           b.txt -> ~/.mw_cache/blobs/yyyy
def _init_cache(cache_dir: Optional[str | Path] = None) -> Path:
    """
    Initializes the cache directory for the MW SDK.

    Args:
        cache_dir (Optional[str | Path]): The path to the cache directory. If not provided, the default cache directory
            will be used.

    Returns:
        None
    """
    if cache_dir is None:
        cache_dir = Path(os.getenv("MW_CACHE_DIR", "~/.cache/mw"))
    if isinstance(cache_dir, str):
        cache_dir = Path(cache_dir)
    print(f"init cache dir: {cache_dir}")
    cache_dir.expanduser().mkdir(parents=True, exist_ok=True)
    cache_dir.expanduser().joinpath("blobs").mkdir(exist_ok=True)
    cache_dir.expanduser().joinpath("datasets").mkdir(exist_ok=True)
    return cache_dir


def download_file(
    id: str,
    filename: str,
    cache_dir: Optional[str | Path] = None,
    token: Optional[str] = None,
) -> Path:
    """Download a file from the dataset.

    Args:
        id (str): The dataset id.
        filename (str): The file name in the dataset.
        cache_dir (Optional[str | Path], optional): The directory to cache the downloaded file. Defaults to None.
        local_dir (Optional[str | Path], optional): The local directory to save the downloaded file. Defaults to None.

    Returns:
        str: The path to the downloaded file.
    """
    if token is None:
        token = os.getenv("MW_TOKEN")
        if not token:
            raise ValueError(
                "No token provided and 'MW_TOKEN' environment variable is not set."
            )
    cache_dir = _init_cache(cache_dir)
    # dataset_detail = get_dataset(id)
    url = f"{HEYWHALE_SITE}/api/datasets/{id}/downloadUrl"
    headers = {
        "x-kesci-token": token,
    }
    response = requests.get(url, headers=headers, timeout=10)
    download_url = None
    if response.status_code == 200:
        files = response.json().get("files")
        for file in files:
            if file.get("Name") + file.get("Ext") == filename:
                download_url = file.get("Url")
                break
        else:
            raise ValueError(f"File '{filename}' not found in dataset '{id}'.")
    else:
        print(response.text)
        response.raise_for_status()
    response = requests.get(download_url, stream=True, timeout=10)
    total_size = int(response.headers.get("content-length", 0))
    chunk_size = 4096  # 4 KB

    # TODO: add file lock
    file_path = (
        Path(cache_dir).expanduser().joinpath("blobs").joinpath(filename + ".lock")
    )
    file_path.parent.mkdir(parents=True, exist_ok=True)
    if file_path.exists():
        # TODO: wait for the lock
        pass
    print("begin to download")
    m = hashlib.md5()
    with open(file_path, "wb") as file:
        for chunk in response.iter_content(chunk_size=chunk_size):
            m.update(chunk)
            file.write(chunk)
            # bar.update(len(chunk))
    etag = m.hexdigest()
    print(f"etag {etag}")
    blob_path = file_path.rename(file_path.parent.joinpath(etag))
    slk_path = (
        Path(cache_dir)
        .expanduser()
        .joinpath("datasets")
        .joinpath(id)
        .joinpath("snapshots")
        .joinpath("1")
        .joinpath(filename)
    )
    slk_path.parent.mkdir(parents=True, exist_ok=True)
    slk_path.symlink_to(blob_path)
    return slk_path
