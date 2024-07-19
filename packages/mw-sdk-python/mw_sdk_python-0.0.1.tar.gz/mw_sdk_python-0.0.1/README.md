# mw-sdk-python

## 简介
`mw-sdk-python` 是一个用于与 Heywhale 平台交互的 Python SDK，旨在简化数据集的获取和管理。

## 安装

```bash
pip install mw-sdk-python
```

## 示例代码

以下是一个示例代码，展示了如何使用 `mw-sdk-python` 获取数据集的详细信息。

```python
from mw-sdk-python.api import get_dataset
# 示例用法
if __name__ == "__main__":
    dataset_id = "替换为你的数据集ID"  # 替换为你的数据集ID
    token = "替换为你的token"  # 替换为你的token或留空以使用MW_TOKEN

    try:
        dataset_details = get_dataset(dataset_id, token)
        print(dataset_details)
    except requests.exceptions.HTTPError as err:
        print(f"HTTP错误: {err}")
    except Exception as err:
        print(f"发生错误: {err}")
```

## 环境变量

- `MW_TOKEN`: 用于身份验证的令牌。如果未提供 token 参数，SDK 将使用此环境变量。
- `HEYWHALE_HOST`: Heywhale 平台的主机地址（可选）。默认值为 `https://www.heywhale.com`。

## 许可证
MIT