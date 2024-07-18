import concurrent.futures
import logging
import os
import threading

import boto3
import click
import pathspec
from boto3.s3.transfer import TransferConfig
from tqdm import tqdm

from tensorkube.constants import REGION


# NOTE: bucket name must be universally unique
# NOTE: bucket name should not be guessable
def create_s3_bucket(bucket_name, region=REGION):
    try:
        s3_client = boto3.client('s3', region_name=region)
        if region is None or region == REGION:
            s3_client.create_bucket(Bucket=bucket_name)
        else:
            location = {'LocationConstraint': region}
            s3_client.create_bucket(Bucket=bucket_name, CreateBucketConfiguration=location)
    except Exception as e:
        click.echo(f"Error creating bucket {bucket_name} in region {region}: {e}")
        return False

    return True


def list_s3_buckets(region: str = REGION):
    try:
        s3 = boto3.client('s3', region_name=region)
        response = s3.list_buckets()
        return response['Buckets']
    except Exception as e:
        click.echo(f"Error listing buckets in region {region}: {e}")
        return []


# TODO!: add a .tensorignore file to ignore files
# def upload_folder_to_bucket(bucket_name, folder_path, region=REGION, s3_path = ""):
#     s3 = boto3.client('s3', region_name=region)
#     for root, dirs, files in os.walk(folder_path):
#         for file in files:
#             if file == ".DS_Store":
#                 continue
#             local_file = os.path.join(root, file)
#             s3_key = s3_path + os.path.relpath(local_file, folder_path).replace(os.sep, '/')
#             s3.upload_file(local_file, bucket_name, s3_key)
#     return True

# Set up logging for debugging
logging.basicConfig(level=logging.INFO)


def upload_file(file_name, bucket_name, s3_key, s3_client, progress_bar):
    def upload_progress(chunk):
        # logging.debug(f"Uploading chunk of {chunk} bytes for {file_name}")
        progress_bar.update(chunk)

    config = boto3.s3.transfer.TransferConfig(use_threads=False)
    try:
        s3_client.upload_file(file_name, bucket_name, s3_key, Callback=upload_progress,
                              Config=config)  # logging.info(f"Successfully uploaded {file_name} to {bucket_name}/{s3_key}")
    except Exception as e:
        logging.error(f"Error uploading {file_name}: {e}")
    finally:
        progress_bar.close()


def load_dockerignore(file_path):
    with open(file_path, 'r') as f:
        patterns = f.read().splitlines()
    return pathspec.PathSpec.from_lines(pathspec.patterns.GitWildMatchPattern, patterns)


def upload_files_in_parallel(bucket_name, folder_path, region='us-east-1', s3_path=''):
    s3_client = boto3.client('s3', region_name=region)
    files_to_upload = []

    dockerignore_filepath = os.path.join(folder_path, '.dockerignore')
    if os.path.exists(dockerignore_filepath):
        spec = load_dockerignore(dockerignore_filepath)
    else:
        spec = pathspec.PathSpec([])

    for root, dirs, files in os.walk(folder_path):
        for file in files:
            local_file = os.path.join(root, file)
            if spec.match_file(local_file):
                continue
            files_to_upload.append(local_file)

    # logging.debug(f"Files to upload: {files_to_upload}")
    progress_bars = {}
    locks = {file: threading.Lock() for file in files_to_upload}

    def upload_with_progress(file_name):
        file_size = os.path.getsize(file_name)
        s3_key = s3_path + os.path.relpath(file_name, folder_path).replace(os.sep, '/')
        # logging.debug(f"Uploading {file_name} to {s3_key} in bucket {bucket_name}")
        with locks[file_name]:
            progress_bars[file_name] = tqdm(total=file_size, unit='B', unit_scale=True, desc=s3_key, leave=True)
        upload_file(file_name, bucket_name, s3_key, s3_client, progress_bars[file_name])

    with concurrent.futures.ThreadPoolExecutor() as executor:
        futures = {executor.submit(upload_with_progress, file): file for file in files_to_upload}
        for future in concurrent.futures.as_completed(futures):
            try:
                future.result()
            except Exception as e:
                logging.error(f"Error in future for {futures[future]}: {e}")

    for progress_bar in progress_bars.values():
        progress_bar.close()


def empty_s3_bucket(bucket_name, region=REGION):
    try:
        s3 = boto3.resource('s3', region_name=region)
        bucket = s3.Bucket(bucket_name)
        bucket.objects.all().delete()
    except Exception as e:
        click.echo(f"Error emptying bucket {bucket_name} in region {region}: {e}")
        return False

    return True


def delete_s3_bucket(bucket_name, region=REGION):
    try:
        click.echo(f"Emptying bucket {bucket_name}...")
        empty_s3_bucket(bucket_name, region)
        click.echo(f"Deleting bucket {bucket_name}...")
        s3 = boto3.client('s3', region_name=region)
        s3.delete_bucket(Bucket=bucket_name)
    except Exception as e:
        click.echo(f"Error deleting bucket {bucket_name} in region {region}: {e}")
        return False

    return True
