'''This module optionally denpends on the `xingyun-GlobalDataManager` entry of [EgorovSystem](https://github.com/FFTYYY/EgorovSystem).
### Egorov System Data Format
    `{path}`
'''
from egorovsystem import get_variable
from typing import Any, Union, Callable, List, TypeAlias
import atexit
from xingyun.savecode.get_code import get_code, filter_default, filter_gitignore, compare_dict, filter_hidden
from .logger import Logger
from .base import get_aws3_dataacess, DataAccess
import warnings

HookType: TypeAlias = Callable[[str,Any,int,dict,str], Any]

def call_hook(hk: HookType, key: str, val: Any, timestamp: int, all_data: dict, modespace: str):
    '''call a hook.
    This function is just to make my auto complete system work when coding.'''
    return hk(key, val, timestamp, all_data, modespace)

def make_hook_logger(logger: Logger):
    '''This is a hook helper funtion. It helps to create a hook that can be used for `GlobalDataManager`.
    '''
    def _logger_hook(key: str, val: str, timestamp: int, all_data: dict, modespace: str):
        if modespace == GlobalDataManager.LOGGER_MODESPACE:
            logger.log(val)
    return _logger_hook

class GlobalDataManager:
    '''This class is used to save all important data of a process. It will automatically upload data to S3. 
        This class will create a meta file under given path to store meta information (list of keys).

    This class optionally denpends on the `xingyun-GlobalDataManager` entry of 
    [EgorovSystem](https://github.com/FFTYYY/EgorovSystem).
    
    ### Egorov System Data Format
        `{path}`
    '''
    METAFILE = "_meta"
    DEFAULT_MODESPACE = "default"
    LOGGER_MODESPACE = "logger"
    LOGGER_KEY = "_log"
    CODE_KEY = "_code"
    EGO_KEY = "xingyun-GlobalDataManager"

    def __init__(self, 
        name: str , 
        hooks: List[HookType] = [] , 
        data_access: DataAccess | None = None , 
        sync_time: int = 50
    ):
        '''
        The intialize function of vlass `GlobalDataManager`.

        ### Parameters
            - name_: the name of the current project.
            - hooks: a list of hooks. Each hook is a callable object that will be called at each time when data updates. 
                The parameters of a hook call is `(key, value, timestamp, all_data, modespace)`. 
                The parameter `modespace` is used to control which hooks to be called.
            - data_access: A `DataAccess` instance to guide how to save data.
            - sync_time: will automatically sync every `sync_time` times. 
        '''

        self.name = name

        # ensure data access
        if data_access is None:
            _my_default_dataacess = get_aws3_dataacess().set_path(get_variable(type(self).EGO_KEY))
            if _my_default_dataacess is None:
                raise RuntimeError("no path. no data in EgorovSystem.")
            data_access = _my_default_dataacess
        self.data_access = data_access.cd(name)

        # initialize / recover data
        self.datas: dict[str, dict[int, Any]] = {}
        self.time_stamps: dict[str, int] = {}
        if not self.download(): # if no remote data, then create a meta entry
            self.update_meta()

        # store hooks
        self.hooks = hooks

        # intialize sync params
        self.sync_time = max(int(sync_time), 1) # ensure no devide by 0
        self._sync_count = 0
    
    def __str__(self):
        return f"<xingyun.GlobalDataManager {self.name}, located at {self.data_access.path}>"
            
    def __del__(self):
        # ensure sync at exit
        try:
            self.upload_data()
        except:
            warnings.warn("final sync failed.")

    def should_sync(self, sync: bool | None):
        ''' Return true one time every `self.sync_time` calls.
        ### Parameters
            - sync: If not `True`, then sync whatever. If not `False`, then don't sync whatever. 
        '''
        self._sync_count = (self._sync_count + 1) % self.sync_time
        if sync is None:
            return self._sync_count == 0
        return sync

    def upload_data(self, keys: list[str] | None = None) -> bool:
        '''Upload data to remote.
        
        ### Parameters
            - keys: the keys of the data to upload. If `None`, then all data.
        '''
        flag = True
        flag = flag and self.update_meta()

        if keys is None:
            keys = list(self.datas)
        for key in keys:
            flag = flag and self.set_remote(key, self.datas.get(key))
        return flag
    
    def update_meta(self) -> bool:
        '''If the meta file is not created, then creat it.'''

        return self.set_remote(GlobalDataManager.METAFILE, {
            "time_stamps": self.time_stamps , 
        })
    
    def download(self):
        '''Read the meta file information and recover data. If no meta file then return `False`.'''

        meta_info = self.get_remote(GlobalDataManager.METAFILE)
        if meta_info is None:
            return False
        
        try:
            time_stamps: dict[str, int] = meta_info["time_stamps"]
        except:
            return False
        
        self.time_stamps = time_stamps
        for key in time_stamps:
            self.datas[key] = self.get_remote(key)


    def update_when_diff(self, 
        key: str, 
        val: Any,
        cmp: Callable[[Any, Any], bool] , 
        modespace: str = DEFAULT_MODESPACE , 
        overwrite: bool = False, 
        force_timestamp: int | None = None, 
        sync: bool | None = None
    ) -> bool:
        '''Set data. But only sets when data is different from stored one.

        ### Parameters
            - force_timestamp: If not `None`, then will force timestamp setting to this value.
            - overwrite: If `True`, will not update timestamp. Else timestamp will be automatically shifted by `1`. 
                If `force_timestamp == True`, then this parameter will not be used.
            - sync: If `True`, then will upload the data to remote. If `None` then use the `autosync` property.
        '''

        time_stamp = self.time_stamps.get(key)
        if force_timestamp is not None: # force time stamp
            time_stamp = force_timestamp

        saved = self.get(key, time_stamp)
        if cmp(saved, val):
            return True
        return self.set(key, val, modespace, overwrite, force_timestamp, sync)

    def set(self, 
        key: str, 
        val: Any, 
        modespace: str = DEFAULT_MODESPACE , 
        overwrite: bool = False, 
        force_timestamp: int | None = None, 
        sync: bool | None = None
    ) -> bool:
        '''Set data. 

        ### Parameters
            - overwrite: If `True`, will not update timestamp. Else timestamp will be automatically shifted by `1`. 
                If `force_timestamp == True`, then this parameter will not be used.
            - force_timestamp: If not `None`, then will force timestamp setting to this value.
            - sync: If `True`, then will upload the data to remote. If `None` then use the `autosync` property.
        '''

        # ensure and update timestamp
        time_stamp = self.time_stamps.get(key)
        if force_timestamp is not None:         # force time stamp anyway
            time_stamp = force_timestamp
        else:
            if time_stamp is None:              # set default time stamp
                time_stamp = 0
            else:
                if not overwrite:               # apply only when time_stamp is already created       
                    time_stamp = time_stamp + 1 # increment time stamp

        self.time_stamps[key] = time_stamp

        # ensure data entry
        if self.datas.get(key) is None:
            self.datas[key] = {}
        data_entry = self.datas.get(key)

        if not isinstance(data_entry, dict):
            raise RuntimeError(f"THIS CAN NEVER HAPPEN.")

        # update data
        data_entry[time_stamp] = val

        # optionally sync data
        flag = True
        if self.should_sync(sync):
            flag = flag and self.upload_data([key])

        # call hooks
        for hk in self.hooks:
            call_hook(hk, key, val, time_stamp, data_entry, modespace)

        return flag
    
    def get(self, key: str, time_stamp: int | None = None):
        '''Get data. If no data return `None`.

        ### Parameters
            - time_stamp: Ask the data at a specific time stamp. If `None`, then default to current time stamp.
        '''
        
        if time_stamp is None:
            time_stamp = self.time_stamps.get(key)

        if time_stamp is None:
            return None
        
        data_entry = self.datas.get(key)
        if data_entry is None:
            return None
        
        return data_entry.get(time_stamp)

    def get_remote(self, key: str):
        return self.data_access.get(key)
    
    def set_remote(self, key: str, val: Any):
        return self.data_access.set(key, val)


    def log(self, content: str, sync: bool | None = None):
        '''This function save data to logger modespace.'''
        return self.set(type(self).LOGGER_KEY, content, modespace = type(self).LOGGER_MODESPACE, sync = sync)

    def get_timestamp(self, key: str) -> int:
        '''Returns the current timestamp of a file. If it is not created, return -1.'''
        t = self.time_stamps.get(key)
        if t is None:
            return -1        
        return t

    def exists(self, key: str):
        return self.datas.get(key) is None

    def summarize(self, key: str, summarize_func: Callable[[dict[int, Any]] , Any]):
        '''Summerize all of the history of a data entry.'''
        data_entry = self.datas.get(key)
        if data_entry is None:
            return None
        return summarize_func(data_entry)
        
    def log_code(self, 
        filters: list[ Callable[[str], bool] ] = [filter_default, filter_gitignore, filter_hidden], 
        sizelimit : int | str = "1mb" , 
        total_sizelimit : int | str = "500mb" , 
        path: str = ".", 
    ):
        '''This function log current code. Only update when there is change in code. Returns code version.'''
        code_data = get_code(filters, sizelimit, total_sizelimit, path)
        self.update_when_diff(type(self).CODE_KEY, code_data, compare_dict, "code")
        return self.get_timestamp(type(self).CODE_KEY)
