# FIST MinIO Client SDK for Python

基于MinIO Python Client SDK 构建 FIST 内部 Py-Client 访问 MinIO 云存储服务

本文将介绍如何安装FIST MinIO Client SDK for Python，并基于`fistminio.fistapi`进行fistminio用户注册，运行简单文件上传和下载示例程序。对于更完整的API以及更多使用示例，请参考[Python Client API Reference](https://min.io/docs/minio/linux/developers/python/API.html)。

假设您已经有一个可运行的 [Python](https://www.python.org/downloads/)开发环境。

> Update history：
> 
> * 2024-01-31 1.0.1 初始版本
> * 2024-04-19 1.0.2 新增外网ip访问

## 最低要求

- Python 3.7或更高版本

## 使用pip安装

```sh
pip install fistminio
```

## 示例-自行注册fistminio用户
需要根据《fistuser使用手册》手册，创建 `fistmino_autousers_keys.yaml`配置文件，再执行`python auto_register.py`

#### auto_register.py

```py
from fistminio.fistapi import register_user

# 自动进行fistminio用户注册
register_user('fistmino_autousers_keys.yaml')
```

#### Run auto_register

```bash
python auto_register.py
```

## 配置 FIST MinIO Client

FIST MinIO client需要以下3个参数来连接 FIST MinIO 对象存储服务。

| 参数     | 描述  |
| :------- | :---- |
| bucket_name | 所在FIST存储服务器上的存储桶名（默认为Username） |
| access_key| Access key是唯一标识你的账户的用户ID  |
| secret_key| Secret key是你账户的密码  |

## 示例-文件夹上传
本示例使用测试用户 wangdc 访问 FIST MinIO 对象存储服务，并上传一个文件文件夹到存储桶中。

#### folder_upload.py

```py
from fistminio.fistapi import init_minio_client, upload_folder

# 替换为自己的access_key和secret_key
access_key="your_access_key"
secret_key="your_secret_key"
client = init_minio_client(access_key, secret_key)

# bucket_name替换为自己的Username
bucket_name = "wangdc"

# 本地需要上传的文件夹路径
source_folder = "C:\\Users\\18058\\Desktop\\youtube"
# FIST存储服务器上的目标文件夹路径，如果没用会自动新建文件夹
target_folder = "youtube/"
# 调用upload_folder上传整个文件
upload_folder(client, bucket_name, source_folder, target_folder)
```

#### Run folder_upload

```bash
python folder_upload.py

Uploading files: 100%|████████████████| 99/99 [00:06<00:00, 15.04it/s]
😀 Upload successful. All contents from the local folder 'C:\Users\18058\Desktop\youtube' have been successfully uploaded to the bucket 'wangdc/youtube/'.
```

## 其他示例

目前`fistminio.fistapi`实现单文件/文件夹上传、下载、删除，更多api待完善。
* [API开发文档参考](https://min.io/docs/minio/linux/developers/python/API.html)

#### single_file_upload.py
```py
from fistminio.fistapi import init_minio_client, fupload

# 替换为自己的access_key和secret_key
access_key="your_access_key"
secret_key="your_secret_key"
client = init_minio_client(access_key, secret_key)

# bucket_name替换为自己的Username
bucket_name = "wangdc"

# 本地需要上传的文件路径
source_file = "tmp/test-file.txt"
# FIST 存储服务器上的目标文件路径
dest_file = "/newfolder/rename-test-file.txt"
# 调用upload上传单个文件
fupload(client, bucket_name, source_file, dest_file)
```



#### single_file_download.py
```py
from fistminio.fistapi import init_minio_client, fdownload

# 替换为自己的access_key和secret_key
access_key="your_access_key"
secret_key="your_secret_key"
client = init_minio_client(access_key, secret_key)

# bucket_name替换为自己的Username
bucket_name = "wangdc"

# FIST存储服务器上需要下载的文件路径
source_file = "CrawlGoogleScholar_v1.rar"
# 目标文件本地路径
dest_file = "tmp/CrawlGoogleScholar_v1.rar"
# 调用fdownload下载单个文件
fdownload(client, bucket_name, source_file, dest_file)
```

#### folder_download.py
```py
from fistminio.fistapi import init_minio_client, download_folder

# 替换为自己的access_key和secret_key
access_key="your_access_key"
secret_key="your_secret_key"
client = init_minio_client(access_key, secret_key)

# bucket_name替换为自己的Username
bucket_name = "wangdc"

# FIST存储服务器上需要下载的文件夹路径
source_folder_prefix = "hmr-master/"
# 目标文件夹本地路径
dest_local_folder_path = "tmp/hmr-master/"
# 调用download_folder下载整个文件夹
download_folder(client, bucket_name, source_folder_prefix, dest_local_folder_path)
```

### single_file_deleted.py
```py
from fistminio.fistapi import init_minio_client, delete_object_from_bucket

# 替换为自己的access_key和secret_key
access_key="your_access_key"
secret_key="your_secret_key"
client = init_minio_client(access_key, secret_key)

# bucket_name替换为自己的Username
bucket_name = "wangdc"

# FIST存储服务器上要删除的目标文件路径
target_file = "youtube/start.bat"
# 调用delete_object_from_bucket删除单个文件
delete_object_from_bucket(client, bucket_name, target_file)
```

### folder_deleted.py
```py
from fistminio.fistapi import init_minio_client, download_folder

# 替换为自己的access_key和secret_key
access_key="your_access_key"
secret_key="your_secret_key"
client = init_minio_client(access_key, secret_key)

# bucket_name替换为自己的Username
bucket_name = "wangdc"

# FIST存储服务器上需要下载的文件夹路径
source_folder_prefix = "hmr-master/"
# 目标文件夹本地路径
dest_local_folder_path = "tmp/hmr-master/"
# 调用download_folder下载整个文件夹
download_folder(client, bucket_name, source_folder_prefix, dest_local_folder_path)
```