'''This module optionally denpends on the `xingyun-getid` entry of [EgorovSystem](https://github.com/FFTYYY/EgorovSystem).
### Egorov System Data Format
    `{path}`
'''
from egorovsystem import get_variable
from typing import Callable, Any
from .base import get_aws3_dataacess, DataAccess

_my_default_dataacess = None

def get_id(
    name: str, 
    data_access: DataAccess | None = None, 
) -> str:
    '''This function ensures every call with the same `path / name` gets a fresh number.
    
    This function optionally denpends on the `xingyun-getid` entry of 
    [EgorovSystem](https://github.com/FFTYYY/EgorovSystem).

    ### Egorov System Data Format
        `{path}`

    ### Parameters
        - name: project name.
        - data_access: A `DataAccess` instance to guide how to save data.
    '''
    global _my_default_dataacess
    if data_access is None:

        if _my_default_dataacess is None:
            try: 
                _my_default_dataacess = get_aws3_dataacess().set_path(get_variable("xingyun-getid"))
            except Exception:
                raise RuntimeError("no meta_path. no egorov system entry.")
        data_access = _my_default_dataacess

    val = data_access.get(name)
    if val is None:
        val = -1
    val = val + 1
    if not data_access.set(name, val):
        raise RuntimeError("set failed.")
    return str(val)
    
    