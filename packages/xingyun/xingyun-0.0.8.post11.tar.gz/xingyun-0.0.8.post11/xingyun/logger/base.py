from typing import Callable, Any
from pathlib import PurePosixPath 
from xingyun.cloud.egorov_awss3 import gets3, sets3
from xingyun.cloud.egorov_dropbox import getdropbox, setdropbox

class DataAccess:
    '''This class defines how to access data that is stored remotely.'''

    def __init__(self,
        path: PurePosixPath | str, 
        get_call: Callable[ [str], Any ] , 
        set_call: Callable[ [str, Any], bool ] , 
    ):
        '''The intialization function of class `DataAccess`.

        ### Parameters
            - path: The name independent path to quries. The actual path will be `path / key`.  
                If `None`, will defaultly use the data saved in the `xingyun-GlobalDataManager` of EgorovSystem.
            - get_call: A callable object. The method to get data remotely. 
                The first parameter of `get_call` should be the **absolute** path of the data.
            - set_call: A callable object. The method to set data remotely. 
                The first parameter of `set_call` should be the **absolute** path of the data. 
                The second parameter of `set_call` should be the value to set. 
                Returns a bool to show if the set is successful.
        '''
        if isinstance(path , str):
            path = PurePosixPath(path)
        self.path = path
        self.get_call = get_call
        self.set_call = set_call

    def cd(self, name: str):
        '''This function returns a copy of `self`, with path updated to `self.path / name`. 
        '''
        return DataAccess(self.path / name, self.get_call, self.set_call)
    
    def set_path(self, new_path: str | PurePosixPath | None):
        '''This function returns a copy of `self`, with path updated to `new_path`. 
        '''
        if new_path is None:
            return None
        if isinstance(new_path , str):
            new_path = PurePosixPath(new_path)
        return DataAccess(new_path, self.get_call, self.set_call)

    def get(self, key: str):
        return self.get_call(str(self.path / key))
    
    def set(self, key: str, val: Any):
        return self.set_call(str(self.path / key), val)

def get_aws3_dataacess():
    return DataAccess(
        PurePosixPath("") , 
        lambda k: gets3(k, format = "pickle"), 
        lambda k,v: sets3(v,k, format = "pickle")
    )

def get_dropbox_dataacess():
    return DataAccess(
        PurePosixPath("") , 
        lambda k: getdropbox(k, format = "pickle"), 
        lambda k,v: setdropbox(v,k, format = "pickle")
    )
