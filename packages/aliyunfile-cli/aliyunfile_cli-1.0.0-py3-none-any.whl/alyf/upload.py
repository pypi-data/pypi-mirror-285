import os
import json
import logging
import hashlib
import requests
from dataclasses import dataclass
from tqdm import tqdm
from tqdm.utils import CallbackIOWrapper

CHUNK_SIZE = 524288

logger = logging.getLogger(__name__)

@dataclass
class UploadContext:
    file_size: int = 0
    url: str = None
    file_id: str = None
    upload_id: str = None
    etag: str = None
    crc64: str = None

def _sha1sum(filename):
    sha1 = hashlib.sha1()
    with open(filename, 'rb') as f:
        while True:
            data = f.read(CHUNK_SIZE)
            if not data:
               break
            sha1.update(data)
    return sha1.hexdigest().upper()

def _create(context, upload_context):
    data = {
        "name":os.path.basename(context.file_path),
        "type":"file",
        "content_type":"application/octet-stream",
        "size":upload_context.file_size,
        "drive_id": context.group_id,
        "parent_file_id":context.folder_id,
        "part_info_list":[{"part_number":1,"part_size":upload_context.file_size,"from":0,"to":upload_context.file_size}],
        "content_hash_name":"sha1",
        "content_hash": _sha1sum(context.file_path),
        "parallel_upload": False,
        "check_name_mode":"refuse",
        "donot_emit_error": True
    }
    headers = {
        'Authorization': f'Bearer {context.token}',
    }
    logger.info('creating upload...')
    create_url = f'https://{context.account_id}.api.aliyunfile.com/v2/file/create'
    response = requests.post(create_url, data=json.dumps(data), headers=headers)
    if response.status_code == 201:
        res = response.json()
        if res.get('exist') == True:
            logger.warning('File exists...')
            raise Exception('Quit due to file exists...')
        else:
            upload_context.upload_url = res['part_info_list'][0]['upload_url']
            upload_context.file_id = res['file_id']
            upload_context.upload_id = res['upload_id']
    else:
        logger.fatal('create failed!')
        logger.fatal(response.status_code)
        logger.fatal(response.text)
        raise Exception('Failed to create upload object...')

def _upload(context, upload_context):
    logger.info('uploading...')
    with open(context.file_path, 'rb') as f:
        with tqdm(total=upload_context.file_size, unit='B', unit_scale=True, desc=context.file_path) as pbar:
            wrapped_file = CallbackIOWrapper(pbar.update, f, "read")
            response = requests.put(upload_context.upload_url, data=wrapped_file)
            if response.status_code == 200:
                upload_context.etag = response.headers['Etag']
                upload_context.crc64 = response.headers['X-Oss-Hash-Crc64ecma']
            else:
                logger.fatal('upload failed!')
                logger.fatal(response.status_code)
                logger.fatal(response.text)
                raise Exception('Failed to upload object...')


def _complete(context, upload_context):
    data = {"drive_id":context.group_id,
            "file_id":upload_context.file_id,
            "upload_id":upload_context.upload_id,
            "part_info_list":[{"part_number":1,"etag":upload_context.etag}],
            "crc64_hash": upload_context.crc64,
            "donot_emit_error":True
            }
    headers = {
        'Authorization': f'Bearer {context.token}',
    }
    logger.info('completing...')
    complete_url = f'https://{context.account_id}.api.aliyunfile.com/v2/file/complete'
    response = requests.post(complete_url, data=json.dumps(data), headers=headers)
    if response.status_code == 200:
        logger.fatal('success')
    else:
        logger.fatal('complete failed!')
        logger.fatal(response.status_code)
        logger.fatal(response.text)
        return
    return

def upload(app_context):
    upload_context = UploadContext()
    file_size = os.path.getsize(app_context.file_path)
    upload_context.file_size = file_size
    _create(app_context, upload_context)
    _upload(app_context, upload_context)
    _complete(app_context, upload_context)


