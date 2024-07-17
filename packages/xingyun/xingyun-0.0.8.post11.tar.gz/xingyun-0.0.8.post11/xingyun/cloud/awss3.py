'''
This module helps easy use AWS S3.
'''

import boto3
import tempfile
import pickle
from typing import Literal, Any
import blosc
import warnings
from .base import CloudAPIBase

class AWSS3(CloudAPIBase):
    def __init__(self, key_id: str, key_sec: str, region: str, bucket: str):
        self.s3 = boto3.client("s3" , 
            region_name             = region ,
            aws_access_key_id       = key_id , 
            aws_secret_access_key   = key_sec , 
        )
        self.bucket = bucket

    def __del__(self):
        try:
            self.s3.close()
        except:
            warnings.warn("close s3 failed.") 

    def set(self, data: Any, tar_path: str, format: Literal["binary" , "str" , "pickle"] = "pickle"):
        '''Set the content of a remote file.

        ### Returns
            Return `True` if success, else return `False`.
        '''
        tar_path = str(tar_path).replace("\\"  , "/")

        if format == "str":
            try:
                data = bytes(str(data), encoding = "utf-8")
                with tempfile.TemporaryFile(mode = "wb+") as fil:
                    fil.write(data)
                    fil.seek(0,0) # 文件指针移动到开头
                    self.s3.upload_fileobj(fil , self.bucket , tar_path)
            except Exception:
                return False
        if format == "pickle":
            data = pickle.dumps(data)
            data = blosc.compress(data) # compress data

        if format == "pickle" or format == "binary":
            try:
                with tempfile.TemporaryFile(mode = "wb+") as fil:
                    fil.write(data)
                    fil.seek(0,0) # 文件指针移动到开头
                    self.s3.upload_fileobj(fil , self.bucket , tar_path)
            except Exception:
                return False

        return True

    def get(self, tar_path: str, format: Literal["binary" , "str" , "pickle"] = "pickle") -> Any:
        '''Get the content of a remote file. 
        
        ### Returns
            Return `None` if fail.
        '''

        tar_path = str(tar_path).replace("\\"  , "/")
        data = None
        if format == "str":
            try:
                with tempfile.TemporaryFile(mode = "wb+") as fil:
                    self.s3.download_fileobj(self.bucket , tar_path, fil)
                    fil.seek(0,0) # 文件指针移动到开头
                    data = fil.read()
                    data = str(data, encoding = "utf-8")
            except Exception:
                return None
        if format == "pickle" or format == "bianry":
            try:
                with tempfile.TemporaryFile(mode = "wb+") as fil:
                    self.s3.download_fileobj(self.bucket , tar_path, fil)
                    fil.seek(0,0) # 文件指针移动到开头
                    data = fil.read()
                    if format == "pickle":
                        try:
                            data = blosc.decompress(data)
                        except: 
                            pass # not blosc compressed. do nothing
                        data = pickle.loads(data)
            except Exception:
                return None
        return data

