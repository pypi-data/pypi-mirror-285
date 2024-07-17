from pathlib import Path
import re
from typing import Callable
import fnmatch
from pathlib import PurePosixPath
from xingyun.universal.convert import convert_size_to_bytes

def filter_default(filename: str):
    '''filter file based on file name.'''

    return re.search(r"((\.py)|(\.sh)|(\.txt))$", filename) is not None


def filter_hidden(filename: str):
    '''skip files that are start with "." .'''

    return re.search(r"(/|^)\.[^\\]", filename) is None

def filter_gitignore(filename: str):
    '''filter out files that are in .gitignore'''

    p = Path(".gitignore")
    if p.exists():
        with open(p, "r") as fil:
            ignore_files = fil.read().split("\n")
        for to_ignore in ignore_files:
            if fnmatch.fnmatch(filename, to_ignore):
                return False
    return True

def get_code(
        filters: list[ Callable[[str], bool] ] = [filter_default, filter_gitignore, filter_hidden], 
        sizelimit : int | str = "1mb" , 
        total_sizelimit  : int | str = "500mb" , 
        path: str = ".", 
    ) -> dict[str, str]:
    '''Get all code files under a dictionary.
    
    ### Parameters
        - path: path to start traverse.
        - pattern: a regular expression to match files.
        - sizelimit: only save files that are lower than size limit.
    '''
    p = Path(path)
    if isinstance(sizelimit , str):
        sizelimit = convert_size_to_bytes(sizelimit)
    if isinstance(total_sizelimit , str):
        total_sizelimit = convert_size_to_bytes(total_sizelimit)

    saved = {}
    acc_size = 0 # accumulated size
    for file in p.rglob("*"):

        # ensure file
        if not file.is_file():
            continue 

        # get relative path
        rel_path = str( PurePosixPath(file.relative_to(p)) )

        if rel_path == "__init__.py":
            import pdb;pdb.set_trace()

        # apply filters
        flag_skip = False
        for filter in filters: # skip if can not pass all filters
            if not filter(rel_path):
                flag_skip = True
        if flag_skip:
            continue


        # apply filesize limit
        file_size = file.stat().st_size
        if file_size > sizelimit: # skip if too large 
            continue

        acc_size = acc_size + file_size
        if acc_size > total_sizelimit: # break if total too large
            break

        # save file content
        with open(file, "rb") as fil:
            content = fil.read()

        try:
            content = content.decode("utf-8")
        except:
            pass
        
        saved[rel_path] = content

    return saved

def compare_dict(dict_1: dict[str, str] | None, dict_2: dict[str, str] | None):
    '''compare if two str dicts are exactly the same.'''

    if (dict_1 is None) or (dict_2 is None):
        return (dict_1 is None) and (dict_2 is None)
    
    names = list( set(dict_1) | set(dict_2) )
    names.sort()
    hash_1 = "##".join([str( dict_1.get(x) ) for x in names])
    hash_2 = "##".join([str( dict_2.get(x) ) for x in names])
    return hash_1 == hash_2
