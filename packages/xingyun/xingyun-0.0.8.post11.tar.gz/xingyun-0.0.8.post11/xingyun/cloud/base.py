'''This module defines the base class of the cloud storage APIs.'''

from abc import ABC, abstractmethod
from typing import Any, Literal

class CloudAPIBase:
    def __init__(self):
        pass 

    @abstractmethod
    def __del__(self):
        pass
        
    @abstractmethod
    def set(self, data: Any, tar_path: str, format: Literal["binary" , "str" , "pickle"] = "pickle") -> bool:
        '''Set the content of a remote file.

        ### Returns
            Return `True` if success, else return `False`.
        '''
        pass
    
    @abstractmethod
    def get(self, tar_path: str, format: Literal["binary" , "str" , "pickle"] = "pickle") -> Any:
        '''Get the content of a remote file. 
        
        ### Returns
            Return `None` if fail.
        '''

        pass 


