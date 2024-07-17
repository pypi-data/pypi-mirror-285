from typing import Any
 
def get_subdict(d: dict[str, Any], prefix: str, splitter: str = "/"):
    '''Find a subdict from a dict.

    ### Example
        >>> dic = {"a": 1, "a/b": 2, "b": 3}
        >>> get_subdict(dic, "a")
        {"b": 2}
    
    '''
    ret = {}
    for x,y in d.items():
        splitted = x.split(splitter)
        if splitted[0] == prefix:
            ret[splitter.join(splitted[1:])] = y
    return ret