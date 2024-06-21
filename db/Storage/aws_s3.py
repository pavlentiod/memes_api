import asyncio
import logging
import os
from functools import cache
from typing import List
from urllib.parse import quote as urlencode

import boto3

from .models import CloudUpload, FileData, UploadFile
from ..config import aws_settings

logger = logging.getLogger(__name__)


class S3(CloudUpload):
    @property
    @cache
    def client(self):
        region_name = aws_settings.AWS_DEFAULT_REGION
        return boto3.client('s3', endpoint_url='https://storage.yandexcloud.net', region_name=region_name)

    async def upload(self, *, file: UploadFile) -> FileData:
        try:
            extra_args = self.config.get('extra_args', {})
            bucket = aws_settings.AWS_BUCKET_NAME
            await asyncio.to_thread(self.client.upload_fileobj, file.file, bucket, file.filename, ExtraArgs=extra_args)
            url = f"https://storage.yandexcloud.net/{bucket}/{urlencode(file.filename.encode('utf8'))}"
            return FileData(url=url, message=f'{file.filename} uploaded successfully', filename=file.filename,
                            content_type=file.content_type, size=file.size)
        except Exception as err:
            logger.error(err)
            print(err)
            return FileData(status=False, error=str(err), message='File upload was unsuccessful')

    async def multi_upload(self, *, files: list[UploadFile]):
        tasks = [asyncio.create_task(self.upload(file=file)) for file in files]
        return await asyncio.gather(*tasks)

    async def list_objects(self, bucket: str) -> List[str]:
        try:
            response = await asyncio.to_thread(self.client.list_objects_v2, Bucket=bucket)
            if 'Contents' in response:
                return [obj['Key'] for obj in response['Contents']]
            else:
                return []
        except Exception as err:
            logger.error(err)
            print(err)
            return []

    async def download_object(self, key: str) -> bytes:
        try:
            bucket = aws_settings.AWS_BUCKET_NAME
            response = await asyncio.to_thread(self.client.get_object, Bucket=bucket, Key=key)
            return await asyncio.to_thread(response['Body'].read)
        except Exception as err:
            logger.error(err)
            print(err)
            return b''
