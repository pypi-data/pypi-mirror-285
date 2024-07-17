'''
This module make using of AWS S3 even easier. It reads the aws access id and 
key from EgorovSystem.

This module denpends on the `aws_access` entry of [EgorovSystem](https://github.com/FFTYYY/EgorovSystem).
### Egorov System Data Format
    "{key_id} {key_sec} {region} {bucket}"
'''

from egorovsystem import Egorov, get_variable
import boto3
from typing import Literal, Any
from .awss3 import AWSS3
import warnings

_awss3_initialized = False
_awss3 = None

def get_awss3_instance():
    global _awss3
    global _awss3_initialized
    
    if not _awss3_initialized:
        try: 
            key_id , key_sec , region , bucket = get_variable("aws_access").split(" ")
            _awss3 = AWSS3(key_id, key_sec, region, bucket)
        except Exception:
            _awss3 = None
    
    return _awss3

def sets3(data: Any, tar_path: str, format: Literal["binary" , "str" , "pickle"] = "pickle"):
    '''This function denpends on the `aws_access` entry of [EgorovSystem](https://github.com/FFTYYY/EgorovSystem).
    ### Egorov System Data Format
        `{key_id} {key_sec} {region} {bucket}`
    '''

    awss3 = get_awss3_instance()
    if awss3 is None:
        warnings.warn("no aws account found. upload fail.")
        return False
    
    return awss3.set(data, tar_path, format)

def gets3(tar_path: str, format: Literal["binary" , "str" , "pickle"] = "pickle") -> Any:
    '''This function denpends on the `aws_access` entry of [EgorovSystem](https://github.com/FFTYYY/EgorovSystem).
    ### Egorov System Data Format
        `{key_id} {key_sec} {region} {bucket}`
    '''

    awss3 = get_awss3_instance()
    if awss3 is None:
        warnings.warn("no aws account found. get fail.")
        return None
    
    return awss3.get(tar_path, format)
