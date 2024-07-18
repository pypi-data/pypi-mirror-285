import os
import yaml
import json

from minio import Minio
from minio.error import MinioAdminException
from minio.credentials import StaticProvider
from minio.minioadmin import MinioAdmin
from minio.error import S3Error
import tempfile

from tqdm import tqdm 
from cryptography.fernet import Fernet

ip = None
page_port = None
api_service_port = None

def init_minio_client(access_key, secret_key, new_ip, new_page_port, new_api_service_port):
    global ip, page_port, api_service_port
    ip = new_ip
    page_port = new_page_port
    api_service_port = new_api_service_port
    return Minio(ip+':'+api_service_port,
                 access_key=access_key,
                 secret_key=secret_key,
                 secure=False)


def check_bucket_exists(client, bucket_name):
    found = client.bucket_exists(bucket_name)
    if not found:
        raise Exception(f"Bucket {bucket_name} not found")
    

def fupload(client, bucket_name, source_file, destination_file):
    """
    Upload a file to a specified bucket on MinIO.

    :param client: Initialized Minio client object.
    :param bucket_name: Name of the MinIO bucket to upload the file to.
    :param source_file: Local path of the file to be uploaded.
    :param destination_file: The destination file name in the bucket.

    Example:
    from fistminio.fistapi import init_minio_client, fupload

    # Replace with your own access_key and secret_key
    access_key = "your_access_key"
    secret_key = "your_secret_key"
    client = init_minio_client(access_key, secret_key)

    # Replace bucket_name with your own Username
    bucket_name = "your_Username"

    # Local file path to upload
    source_file = "path/to/your/file"
    # Target file path on the FIST storage server
    dest_file = "path/in/bucket/to/file"
    # Call fupload to upload a single file
    fupload(client, bucket_name, source_file, dest_file)

    """
    check_bucket_exists(client, bucket_name)
    client.fput_object(bucket_name, destination_file, source_file)
    print(f"\U0001F600 successfully uploaded. {source_file} uploaded as object {destination_file} to {bucket_name} bucket")


def fdownload(client, bucket_name, source_file, destination_file):
    """
    Download a single object from a MinIO bucket.

    :param client: Initialized Minio client object.
    :param bucket_name: Name of the MinIO bucket to download the object from.
    :param source_file: The name of the source file in the bucket to be downloaded.
    :param destination_file: The local destination file path where the object will be saved.

    Example:
    from fistminio.fistapi import init_minio_client, fdownload

    # Replace with your own access_key and secret_key
    access_key = "your_access_key"
    secret_key = "your_secret_key"
    client = init_minio_client(access_key, secret_key)

    # Replace bucket_name with your own Username
    bucket_name = "your_Username"

    # The file path to be downloaded from the FIST storage server
    source_file = "path/to/your/file"
    # The target local file path
    dest_file = "path/to/your/local/file"
    # Call fdownload to download a single file
    fdownload(client, bucket_name, source_file, dest_file)
    """
    check_bucket_exists(client, bucket_name)
    client.fget_object(bucket_name, source_file, destination_file)
    print(f"\U0001F600 successfully downloaded. {source_file} downloaded as object from {bucket_name} bucket to local {destination_file}")


def add_user_to_group(minio_admin_client, user_name, group_name):
    try:
        group_info = minio_admin_client.group_info(group_name)
        group_info = json.loads(group_info)
        group_members = group_info['members']
    except MinioAdminException:
        raise Exception(f"group_name {group_name} not found")

    if user_name not in group_members:
        group_members.append(user_name)
        minio_admin_client.group_add(group_name, group_members)
    else:
        raise Exception(f"user_name {user_name} already in {group_name}")
    

def upload_text_as_file(client, bucket_name, text_content, destination_file):
    """
    Save the text content to a temporary file and then upload it to the MinIO bucket.

    :param client: Initialized Minio client object.
    :param bucket_name: The name of the MinIO bucket.
    :param text_content: The text content to be uploaded.
    :param destination_file:The name of the target file in the bucket.
    """
    with tempfile.NamedTemporaryFile(delete=False, mode='w+') as temp_file:
        temp_file.write(text_content)
        temp_file.flush()
        fupload(client, bucket_name, temp_file.name, destination_file)


def auto_create_users(minio_client, minio_admin_client, user_name, password, group_name):
    """
    Automatically create a new user, add the user to a specified group, create a bucket for the user, and upload a README.md file to the new bucket.

    :param minio_client: Initialized Minio client object.
    :param minio_admin_client: Initialized MinioAdmin client object.
    :param user_name: The username for the new user.
    :param password: The password for the new user.
    :param group_name: The name of the group to add the new user to.
    """
    minio_admin_client.user_add(user_name, password)
    add_user_to_group(minio_admin_client, user_name, group_name)
    minio_client.make_bucket(user_name)
    text_content = f"Welcome {user_name}. Please access the console through the browser at http:{ip}:{page_port}, Username: {user_name}, Password: {password}. \
                    \nYou can also apply for Access Keys in the console using Minio Client and fistminio SDK"
    destination_file = "access_info.txt"  # The name of the file saved in the bucket
    upload_text_as_file(minio_client, user_name, text_content, destination_file)
    print(f"User created successfully. Please access the console through the browser at http:{ip}:{page_port}, Username: {user_name}, Password: {password}")


def register_user(yaml_file_path, new_ip, new_page_port, new_api_service_port):
    """
    Register a new user in the MinIO server by reading encrypted credentials from a YAML file, decrypting them, and creating a new user and bucket.

    :param yaml_file_path: Path to the YAML file containing encrypted MinIO access and secret keys.

    Example:
    from fistminio.fistapi import register_user

    # Automatically register a user in fistminio
    register_user('fistmino_autousers_keys.yaml')
    """
    global ip, page_port, api_service_port
    ip = new_ip
    page_port = new_page_port
    api_service_port = new_api_service_port
    
    with open(yaml_file_path, 'r') as yaml_file:
        encrypted_data = yaml.safe_load(yaml_file)

    cipher_suite = Fernet(encrypted_data['key'].encode())
    decrypted_access_key = cipher_suite.decrypt(encrypted_data['encoder_access_key'].encode()).decode()
    decrypted_secret_key = cipher_suite.decrypt(encrypted_data['encoder_secret_key'].encode()).decode()

    minio_client = init_minio_client(decrypted_access_key, decrypted_secret_key)
    minio_admin_client = MinioAdmin(endpoint=ip+':'+api_service_port,
                                    credentials=StaticProvider(access_key=decrypted_access_key,
                                                               secret_key=decrypted_secret_key),
                                    secure=False)

    username = input("Please enter a username (3-63 Lowercase characters): ")
    while not (3 <= len(username) <= 63 and username.isascii() and username.isalnum() or "_" in username):
        print("The username must be between 3 to 63 ASCII Lowercase characters, please re-enter.")
        username = input("Please enter a username (3-63 Lowercase characters):")
    password = username + '123456'
    auto_create_users(minio_client, minio_admin_client, username, password, "fistgroup")


def upload_folder(minio_client, bucket_name, folder_path, target_folder):
    """
    Upload all contents of a local folder to a specified folder in a MinIO bucket.

    :param minio_client: Initialized Minio client object.
    :param bucket_name: Name of the MinIO bucket where the folder will be uploaded.
    :param folder_path: Local path of the folder whose contents are to be uploaded.
    :param target_folder: Target folder path inside the MinIO bucket.

    Example:
    from fistminio.fistapi import init_minio_client, upload_folder

    # Replace with your own access_key and secret_key
    access_key = "your_access_key"
    secret_key = "your_secret_key"
    client = init_minio_client(access_key, secret_key)

    # Replace bucket_name with your own Username
    bucket_name = "your_Username"

    # Local folder path to upload
    source_folder = "path/to/your/local/folder"
    # Target folder path on the FIST storage server, it will be created if it doesn't exist
    target_folder = "your_folder/"
    # Call upload_folder to upload the entire folder
    upload_folder(client, bucket_name, source_folder, target_folder)
    """
    if not os.path.isdir(folder_path):
        raise ValueError(f"The provided folder path '{folder_path}' does not exist, please confirm if the path '{folder_path}' is correct.")
    
    files_to_upload = []  # Store the path of all files to be uploaded
    for root, dirs, files in os.walk(folder_path):
        for filename in files:
            local_path = os.path.join(root, filename)
            files_to_upload.append(local_path)
    
    if not files_to_upload:
        raise Warning(f"The folder path '{folder_path}' is empty")
    else:
        for local_path in tqdm(files_to_upload, desc="Uploading files"):
            relative_path = os.path.relpath(local_path, folder_path)
            minio_path = os.path.join(target_folder, relative_path).replace("\\", "/")
            minio_client.fput_object(bucket_name, minio_path, local_path)
        
        print(f"\U0001F600 Upload successful. All contents from the local folder '{folder_path}' have been successfully uploaded to the bucket '{bucket_name}/{target_folder}'.")


def download_folder(minio_client, bucket_name, folder_prefix, local_folder_path):
    """
    Download all objects with a specific prefix (folder) from a MinIO bucket.

    :param minio_client: Initialized Minio client object.
    :param bucket_name: Name of the MinIO bucket.
    :param folder_prefix: Prefix of the folder to download objects from.
    :param local_folder_path: Local path to save the downloaded folder content.

    Example:
    from fistminio.fistapi import init_minio_client, delete_folder_from_bucket

    # Replace with your own access_key and secret_key
    access_key = "your_access_key"
    secret_key = "your_secret_key"
    client = init_minio_client(access_key, secret_key)

    # Replace bucket_name with your own Username
    bucket_name = "your_Username"

    # The folder path to be downloaded on the FIST storage server
    source_folder_prefix = "your_folder/"
    # Target folder local path
    dest_local_folder_path = "path/to/your/local/folder/"
    # Call download_folder to download the entire folder
    download_folder(client, bucket_name, source_folder_prefix, dest_local_folder_path)
    """
    try:
        objects = list(minio_client.list_objects(bucket_name, prefix=folder_prefix, recursive=True))
        if not objects:
            raise Exception(f"The bucket '{folder_prefix}' is empty, please confirm if the folder_prefix is correct")

        # import pdb;pdb.set_trace()
        
        for obj in tqdm(objects, desc="Downloading files"):
            # Construct the relative path of the object within the folder_prefix
            relative_path = os.path.relpath(obj.object_name, folder_prefix)
            # Construct the full local path to save the file
            local_file_path = os.path.normpath(os.path.join(local_folder_path, relative_path)).replace("\\", "/")

            # Ensure local directory structure exists
            # import pdb;pdb.set_trace()
            os.makedirs(os.path.dirname(local_file_path), exist_ok=True)
            minio_client.fget_object(bucket_name, obj.object_name, local_file_path)
        print(f"\U0001F600 Download successful. All contents from the bucket '{bucket_name}/{folder_prefix}' have been successfully downloaded to the local directory '{local_folder_path}'.")
    except S3Error as err:
        print(err)


def delete_object_from_bucket(minio_client, bucket_name, object_name):
    """
    Delete a specific object from a MinIO bucket.

    :param minio_client: Initialized Minio client object.
    :param bucket_name: Name of the MinIO bucket from which the object will be deleted.
    :param object_name: The name of the object to be deleted.

    Example:
    from fistminio.fistapi import init_minio_client, delete_object_from_bucket

    # Replace with your own access_key and secret_key
    access_key = "your_access_key"
    secret_key = "your_secret_key"
    client = init_minio_client(access_key, secret_key)

    # Replace bucket_name with your own Username
    bucket_name = "your_Username"

    # The target file path to be deleted on the FIST storage server
    target_file = "path/to/your/file"
    # Call delete_object_from_bucket to delete a single file
    delete_object_from_bucket(client, bucket_name, target_file)
    """
    try:
        minio_client.remove_object(bucket_name, object_name)
        print(f"\U0001F600 Successfully deleted. '{object_name}' has been deleted from the '{bucket_name}' bucket.")
    except S3Error as exc:
        print("Error occurred while deleting object:", exc)


def delete_folder_from_bucket(minio_client, bucket_name, folder_path):
    """
    Delete a folder and all its contents from a MinIO bucket.

    :param minio_client: Initialized Minio client object.
    :param bucket_name: Name of the MinIO bucket from which the folder and its contents will be deleted.
    :param folder_path: The path of the folder to be deleted. Ensure it ends with a slash ('/') to denote a folder.

    Example:
    from fistminio.fistapi import init_minio_client, delete_folder_from_bucket

    # Replace with your own access_key and secret_key
    access_key = "your_access_key"
    secret_key = "your_secret_key"
    client = init_minio_client(access_key, secret_key)

    # Replace bucket_name with your own Username
    bucket_name = "your_Username"

    # Destination folder path to be deleted on the FIST storage server
    target_folder = "path/to/your/folder/"
    # Call delete_folder_from_bucket to delete the entire folder
    delete_folder_from_bucket(client, bucket_name, target_folder)
    """
    try:
        if not folder_path.endswith("/"):
            folder_path += "/"

        objects_to_delete = list(minio_client.list_objects(bucket_name, prefix=folder_path, recursive=True))
        total_objects = len(objects_to_delete)

        if total_objects == 0:
            print("The object to be deleted was not found.")
            return

        for obj in tqdm(objects_to_delete, desc="Deleting files", total=total_objects):
            minio_client.remove_object(bucket_name, obj.object_name)
            # print(f"'{obj.object_name}' has been deleted from the '{bucket_name}' bucket.")

        print(f"\U0001F600 Successfully deleted. The folder '{folder_path}' and all its contents have been deleted from the '{bucket_name}' bucket.")
    except S3Error as exc:
        print("Error occurred while deleting object:", exc)