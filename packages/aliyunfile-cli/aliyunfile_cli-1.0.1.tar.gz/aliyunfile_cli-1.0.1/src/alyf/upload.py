import os
import json
import crcmod
import logging
import hashlib
import requests
from dataclasses import dataclass
from tqdm import tqdm

MD5_CHUNK_SIZE = 524288
SLICING_SIZE = 1024 * 1024 * 10
CRC_CHUNK_SIZE = 52428800

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)

@dataclass
class UploadContext:
    file_size: int = 0
    url: str = None
    file_id: str = None
    upload_id: str = None
    slices = []

def _sha1sum(filename):
    logger.info('calculating md5...')
    sha1 = hashlib.sha1()
    with open(filename, 'rb') as f:
        while True:
            data = f.read(MD5_CHUNK_SIZE)
            if not data:
               break
            sha1.update(data)
    return sha1.hexdigest().upper()

def _slicing(upload_context):
    part_number = 1
    slices = []
    start = 0
    end = upload_context.file_size if upload_context.file_size <= SLICING_SIZE else SLICING_SIZE
    while True:
        slices.append({"part_number":part_number,"part_size":end - start,"from":start,"to":end})
        part_number += 1
        start = end
        if start == upload_context.file_size:
            break
        end += SLICING_SIZE
        if end > upload_context.file_size:
            end = upload_context.file_size
    upload_context.slices = slices

def _create(context, upload_context):
    data = {
        "name":os.path.basename(context.file_path),
        "type":"file",
        "content_type":"application/octet-stream",
        "size":upload_context.file_size,
        "drive_id": context.group_id,
        "parent_file_id":context.folder_id,
        "part_info_list": upload_context.slices,
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
        if res.get('exist') == True or res.get('part_info_list') is None:
            logger.warning('File exists...')
            raise Exception('Quit due to file exists...')
        else:
            for index, item in enumerate(res['part_info_list']):
                upload_context.slices[index]['upload_url'] = item['upload_url']
            upload_context.file_id = res['file_id']
            upload_context.upload_id = res['upload_id']
    else:
        logger.fatal('create failed!')
        logger.fatal(response.status_code)
        logger.fatal(response.text)
        raise Exception('Failed to create upload object...')

def _read_byte_range(file_path, start, end):
    with open(file_path, 'rb') as file:
        file.seek(start)
        data = file.read(end - start)
    return data

def _upload(context, upload_context):
    logger.info('uploading...')
    with open(context.file_path, 'rb') as f:
        pbar = tqdm(total=upload_context.file_size, unit='B', unit_scale=True, unit_divisor=1024)
        for slice in upload_context.slices:
            wrapped_file = _read_byte_range(context.file_path, slice['from'], slice['to'])
            response = requests.put(slice['upload_url'], data=wrapped_file)
            pbar.update(slice['to'] - slice['from'])
            if response.status_code == 200:
                slice['etag'] = response.headers['Etag']
            else:
                logger.fatal('upload failed!')
                logger.fatal(response.status_code)
                logger.fatal(response.text)
                raise Exception('Failed to upload object...')

def compute_crc64(file_path):
    crc64_func = crcmod.mkCrcFun(0x142F0E1EBA9EA3693, initCrc=0, xorOut=0xffffffffffffffff, rev=True)
    crc64 = 0
    with open(file_path, 'rb') as f:
        for chunk in iter(lambda: f.read(CRC_CHUNK_SIZE), b''):
            crc64 = crc64_func(chunk, crc64)
    return str(crc64)

def _complete(context, upload_context):
    data = {"drive_id":context.group_id,
            "file_id":upload_context.file_id,
            "upload_id":upload_context.upload_id,
            "part_info_list":[{"part_number":c['part_number'],"etag":c['etag']} for c in upload_context.slices],
            "crc64_hash": compute_crc64(context.file_path),
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
    _slicing(upload_context)
    _create(app_context, upload_context)
    _upload(app_context, upload_context)
    _complete(app_context, upload_context)


