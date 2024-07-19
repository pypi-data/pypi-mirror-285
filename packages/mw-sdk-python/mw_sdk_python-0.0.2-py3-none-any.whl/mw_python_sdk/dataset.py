from dataclasses import dataclass
from datetime import datetime

# UploadInfo 代表上传需要的信息
@dataclass(frozen=True)
class UploadInfo:
    ak: str
    sk: str
    token: str  # upload token
    endpoint: str  # endpoint
    region: str  # region
    bucket: str  # 上传的 bucket
    prefix_to_save: str  # 文件上传目录 组成结构为: dataset / user ID /


# DatasetFile 代表一个s3上的文件
@dataclass(frozen=True)
class DatasetFile:
    _id: str
    key: str
    size: int


# Dataset 代表一个数据集
@dataclass(frozen=True)
class Dataset:
    _id: str
    title: str
    short_description: str
    folder_name: str
    files: list[DatasetFile]
    created_at: datetime
    updated_at: datetime
