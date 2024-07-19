import boto3
import os
from PIL import Image
import pathlib
from io import BytesIO
from pathlib import Path
import pathlib
# from zappa.asynchronous import task
import requests

class S3ImageVariant():
    """_summary_
    """

    def __init__(self, src_bucket, dest_bucket=None, src_prifix="", dest_prifix="images/"):
        """_summary_

        Args:
            src_bucket (_type_): _description_
            dest_bucket (_type_, optional): _description_. Defaults to None.
            src_prifix (str, optional):  "".
            dest_prifix (str, optional): _description_. Defaults to "images/".
        """
        if not src_bucket or not src_prifix.endswith("/"):
            raise Exception("需要正确设置路径前缀，如: original_images/")
        elif src_prifix == dest_prifix and src_bucket == dest_bucket:
            raise Exception("同一个bucket的情况下，目标前缀和源前缀不能相同")
        else:
            self.src_bucket = src_bucket
            self.dest_bucket = dest_bucket or self.src_bucket
            self.s3_client = boto3.client('s3')
            self.s3 = boto3.resource('s3')
            self.src_prifix = src_prifix
            self.dest_prifix = dest_prifix

    def resize_image(self, src_key, dest_key, size):
        print(f"开始转换图片，源key: {src_key} -> {dest_key}" )
        in_mem_file = BytesIO()
        
        s3Object = self.s3_client.get_object(
            Bucket=self.src_bucket, Key=src_key)

        content_type = s3Object['ContentType']
        if 'image/jpeg' != content_type:
            print(f"不是图片，跳过处理 content_type : {content_type}")
        else:
            file_byte_string = s3Object['Body'].read()
            im = Image.open(BytesIO(file_byte_string))
            im.thumbnail(size, Image.ANTIALIAS)
            # ISSUE : https://stackoverflow.com/questions/4228530/pil-thumbnail-is-rotating-my-image
            im.save(in_mem_file, format=im.format)
            in_mem_file.seek(0)

            response = self.s3_client.put_object(
                Body=in_mem_file,
                Bucket=self.dest_bucket,
                Key=dest_key
            )

    def onCreateObject(self, key):
        """lambda  入口"""
        size1 = (200, 200)
        # url字符转换
        _src_key = requests.utils.unquote(key)
        
        if key.startswith(self.src_prifix):
            realKey = key[len(self.src_prifix):]
            dest_key = requests.utils.unquote(self.dest_prifix + realKey+f".{size1[0]}x{size1[1]}")
            self.resize_image(
                src_key=_src_key,
                dest_key=dest_key,
                size=size1)
