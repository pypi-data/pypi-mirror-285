import io
import os
import time
import urllib.parse
from pathlib import Path

import boto3
import requests

from dalpha.logging import logger
from dalpha.logging.events import Event

s3_client = boto3.client('s3')
mai_s3_endpoint_url = os.environ.get('MAI_S3_ENDPOINT_URL')
mai_s3_client = boto3.client(
    's3',
    aws_access_key_id=os.environ.get('MAI_S3_ACCESS_KEY_ID'),
    aws_secret_access_key=os.environ.get('MAI_S3_SECRET_ACCESS_KEY'),
    endpoint_url = mai_s3_endpoint_url,
    config = boto3.session.Config(signature_version='s3v4')
)

def download_from_url(url):
    r = requests.get(url, stream=True)
    if r.status_code != 200:
        raise Exception(f"can't download from url {r.status_code} : {r.text}")
    else:
        return io.BytesIO(r.content)

def download_from_s3(bucket, key, download_path):
    try:
        s3_client.download_file(bucket, key, download_path)
    except Exception as e:
        raise Exception(f"failed to download from s3\n{e}")
    
def get_key_from_s3_url(s3_url: str, bucket: str):
    parsed_url = urllib.parse.urlparse(s3_url)
    path = parsed_url.path.lstrip('/') # .com, .so 이후, params와 query 이전까지의 부분.
    
    # "https://버킷.s3.ap-northeast-2.amazonaws.com/키" 형태
    if "s3.ap-northeast-2.amazonaws.com" in s3_url and bucket in parsed_url.netloc:
        key = path
    # "https://media.dalpha.so/버킷/키" 형태
    elif "media.dalpha.so" in s3_url:
        bucket_index = path.index(bucket)
        key = path[bucket_index + len(bucket):].lstrip('/')
    else:
        raise ValueError(f"invalid s3 url: {s3_url}")
        
    return key
        
    
def download_from_s3_url(bucket: str, url: str, download_path: str | Path):
    try:
        key = get_key_from_s3_url(url, bucket)
    except ValueError as e:
        raise Exception(f"failed to get key from s3 url\n{e}")
    
    download_from_s3(bucket, key, str(download_path))
        
    
def upload_s3(upload_path, bucket, key = None, account_id = None):
    if key is None and account_id is not None:
        if not isinstance(account_id, int): raise TypeError('account_id is not a int')
        key = f"channel_id={account_id}/{time.strftime('y=%Y/m=%m/d=%d', time.localtime(time.time()))}/{os.path.basename(upload_path)}"
    try:
        s3_client.upload_file(upload_path, bucket, key)
        logger.info(
            message = f"uploaded to s3://{bucket}/{key}",
            event = Event.UPLOAD_S3,
        )
        return os.path.join(f"https://{bucket}.s3.ap-northeast-2.amazonaws.com", key)
    except Exception as e:
        raise Exception(f"failed to upload s3\n{e}")

def upload_s3_image(pil_image, bucket, img_save_name = None, key = None, account_id = None):
    '''
    pil_image : PIL.Image
    bucket : S3에 업로드할 버킷 이름
    img_save_name : S3에 저장될 이미지 파일 이름
    key : S3에 저장될 이미지 파일 경로
    account_id : S3에 저장될 이미지 파일 경로에 포함될 account_id
    '''
    img_byte_arr = io.BytesIO()
    if img_save_name is None and key is None:
        raise ValueError("img_save_name or key is required")
    if img_save_name is not None:
        if not isinstance(account_id, int): raise TypeError('account_id is not a int')
        output_file_extension = img_save_name.split('.')[-1]
        key = f"channel_id={account_id}/{time.strftime('y=%Y/m=%m/d=%d', time.localtime(time.time()))}/{img_save_name}"
    else:
        output_file_extension = key.split('.')[-1]
    
    pil_image.save(img_byte_arr, format=str(output_file_extension).upper())
    img_byte_arr = img_byte_arr.getvalue()
    
    try:
        s3_client.put_object(Body=img_byte_arr, Bucket=bucket, Key=key)
        logger.info(
            message = f"uploaded to s3://{bucket}/{key}",
            event = Event.UPLOAD_S3,
        )
        return os.path.join(f"https://{bucket}.s3.ap-northeast-2.amazonaws.com", key)
    except Exception as e:
        raise Exception(f"failed to upload s3\n{e}")

def download_from_mai_s3(bucket, key, download_path):
    try:
        mai_s3_client.download_file(bucket, key, download_path)
    except Exception as e:
        raise Exception(f"failed to download from mai_s3\n{e}")
    
def upload_mai_s3(upload_path, bucket, key = None, account_id = None):
    if key is None and account_id is not None:
        if not isinstance(account_id, int): raise TypeError('account_id is not a int')
        key = f"channel_id={account_id}/{time.strftime('y=%Y/m=%m/d=%d', time.localtime(time.time()))}/{os.path.basename(upload_path)}"
    try:
        mai_s3_client.upload_file(upload_path, bucket, key)
        logger.info(
            message = f"uploaded to s3://{bucket}/{key}",
            event = Event.UPLOAD_S3,
        )
        return os.path.join(mai_s3_endpoint_url, bucket, key)
    except Exception as e:
        raise Exception(f"failed to upload s3\n{e}")
    
def upload_mai_s3_image(pil_image, bucket, img_save_name = None, key = None, account_id = None):
    '''
    pil_image : PIL.Image
    bucket : S3에 업로드할 버킷 이름
    img_save_name : S3에 저장될 이미지 파일 이름
    key : S3에 저장될 이미지 파일 경로
    account_id : S3에 저장될 이미지 파일 경로에 포함될 account_id
    '''
    img_byte_arr = io.BytesIO()
    if img_save_name is None and key is None:
        raise ValueError("img_save_name or key is required")
    if img_save_name is not None:
        if not isinstance(account_id, int): raise TypeError('account_id is not a int')
        output_file_extension = img_save_name.split('.')[-1]
        key = f"channel_id={account_id}/{time.strftime('y=%Y/m=%m/d=%d', time.localtime(time.time()))}/{img_save_name}"
    else:
        output_file_extension = key.split('.')[-1]
    
    pil_image.save(img_byte_arr, format=str(output_file_extension).upper())
    img_byte_arr = img_byte_arr.getvalue()
    
    try:
        mai_s3_client.put_object(Body=img_byte_arr, Bucket=bucket, Key=key)
        logger.info(
            message = f"uploaded to s3://{bucket}/{key}",
            event = Event.UPLOAD_S3,
        )
        return os.path.join(mai_s3_endpoint_url, bucket, key)
    except Exception as e:
        raise Exception(f"failed to upload s3\n{e}")
