import os
from os import getenv
from sys import argv
import boto3
import shutil
import re

BUCKET_NAME = "wiliot-partner-pkg"


VERSION = ".".join(os.getenv("version").split(".")[:-1]).split("+")[0]


def delete_argv_folders():
    folders_to_delete = ['internal', 'wiliot.egg-info']
    for folder in os.getenv('DELETED_FOLDERS').split(','):
        folders_to_delete.append(folder)

    files = [f for f in os.listdir('.') if os.path.isfile(f)]
    for f in files:
        if f == "setup.py" or "ci.py":
            pass
        else:
            os.remove(f)
            print(f"Deleting the '{f}' file")

    for root, subdirs, files in os.walk("wiliot/"):
        for folder in folders_to_delete:
            if re.search(f".*{folder}.*", root):
                print(f"Deleting the '{root}' folder")
                shutil.rmtree(root)


def upload_latest_version(filepath: str, filename: str, partner_name: str):
    s3.meta.client.upload_file(filepath, 'wiliot-partner-pkg', f'{partner_name}/latest/{filename}')
    print("Uploaded: ", filepath, 'wiliot-partner-pkg', f'{partner_name}/latest/{filename}')
    s3.meta.client.upload_file(filepath, 'wiliot-partner-pkg', f'{partner_name}/previous_releases/{filename}')
    print("Uploaded: ", filepath, 'wiliot-partner-pkg', f'{partner_name}/previous_releases/{filename}')


def earth_latest_folder(partner_name: str):
    bucket = s3.Bucket(BUCKET_NAME)
    for obj in bucket.objects.filter(Prefix=f'{partner_name}/latest/'):
        old_filename = obj.key.split("/")[2]
        print(s3.meta.client.delete_object(Bucket=BUCKET_NAME, Key=f'{partner_name}/latest/{old_filename}'))


def release_version(partner_name: str):
    filename = f'wiliot-{".".join(os.getenv("version").split("."))}.tar.gz'
    filename_in_bucket = f'wiliot-{VERSION}+{os.getenv("BITBUCKET_BUILD_NUMBER")}.tar.gz'
    print(os.getenv("version"))
    print(filename, partner_name, filename_in_bucket)
    earth_latest_folder(partner_name)
    upload_latest_version(f'dist/{filename}', filename_in_bucket, partner_name)


def safe_list_get(li, index, default_value=None):
    try:
        return li[index]
    except IndexError:
        return default_value


if __name__ == '__main__':
    if safe_list_get(argv, 1) == "DELETED_FOLDERS":
        delete_argv_folders()
    else:
        s3 = boto3.resource("s3",
                            aws_access_key_id=getenv("AWS_ACCESS_KEY_ID"),
                            aws_secret_access_key=getenv("AWS_SECRET_ACCESS_KEY"),
                            aws_session_token=getenv("AWS_SESSION_TOKEN"))
        release_version(os.getenv("PARTNER_NAME"))
