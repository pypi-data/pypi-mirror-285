'''
This module helps easy use AWS S3.
'''

import dropbox
import tempfile
import pickle
from typing import Literal, Any
import blosc
import warnings
from .base import CloudAPIBase

class Dropbox(CloudAPIBase):
    def __init__(self, app_key: str, app_secret: str, refresh_token: str):
        self.dropbox = dropbox.Dropbox(
            app_key = app_key,
            app_secret = app_secret , 
            oauth2_refresh_token = refresh_token , 
        )

    def __del__(self):
        try:
            self.dropbox.close()
        except:
            warnings.warn("close dropbox failed.") 

    def set(self, data: Any, tar_path: str, format: Literal["binary" , "str" , "pickle"] = "pickle"):
        '''Set the content of a remote file.

        ### Returns
            Return `True` if success, else return `False`.
        '''
        tar_path = str(tar_path).replace("\\"  , "/")
        if not tar_path.startswith("/"):
            tar_path = "/" + tar_path

        if format == "str":
            try:
                data = bytes(str(data), encoding = "utf-8")
                self.dropbox.files_upload(data, tar_path, dropbox.files.WriteMode.overwrite)

            except Exception:
                return False
            
        if format == "pickle":
            data = pickle.dumps(data)
            data = blosc.compress(data) # compress data

        if format == "pickle" or format == "binary":
            try:
                self.dropbox.files_upload(data, tar_path, dropbox.files.WriteMode.overwrite)
            except Exception:
                return False

        return True

    def get(self, tar_path: str, format: Literal["binary" , "str" , "pickle"] = "pickle") -> Any:
        '''Get the content of a remote file. 
        
        ### Returns
            Return `None` if fail.
        '''

        tar_path = str(tar_path).replace("\\"  , "/")
        if not tar_path.startswith("/"):
            tar_path = "/" + tar_path

        data = None
        if format == "str":
            try:
                file = self.dropbox.files_download(tar_path)
                data = str(file[1].content, encoding = "utf-8")
            except Exception:
                return None
            
        if format == "pickle" or format == "bianry":
            try:
                file = self.dropbox.files_download(tar_path)
                data = file[1].content
                if format == "pickle":
                    try:
                        data = blosc.decompress(data)
                    except: 
                        pass # not blosc compressed. do nothing
                data = pickle.loads(data)
            except Exception:
                return None
        return data

