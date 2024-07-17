import sys
from typing import Callable, Any
import re
import warnings
from argparse import Namespace
from ..random.my_random import my_randint
from ..universal.get_subdict import get_subdict

class Condition:
    def __init__(self, condition: Callable[[ dict[str, Any] ], bool] = lambda _: True):
        self.condition = condition

    def test(self, config: dict[str, Any]):
        return self.condition(config)
    
    def __and__(self, other: "Condition"):
        return Condition(lambda v: self.condition(v) and other.condition(v))
    
    def __or__(self, other: "Condition"):
        return Condition(lambda v: self.condition(v) or other.condition(v))
    
    @classmethod
    def and_all(cls, conditions: list["Condition"]):
        r = Condition()
        for c in conditions:
            r = r & c
        return r


condition_env = {}
class PreCondition:
    def __init__(self, dependence_list: list [str], cond: Callable[... , bool]):

        cond_exists = Condition(lambda C: not (False in [x in C for x in dependence_list]) )
        cond_user   = Condition(lambda C: cond(*[C[x] for x in dependence_list]))

        self.cond = cond_exists & cond_user
        self.id = my_randint(0,2333333)
    def __enter__(self):
        condition_env[self.id] = self.cond
    def __exit__(self, *arg, **kwarg):
        condition_env.pop(self.id)

class MyDict(dict):
    def __init__(self, d: dict = {}):
        super().__init__(d)

    def sub(self, prefix: str, splitter: str = "/"):
        return MyDict( get_subdict(self, prefix, splitter) )
    
    def __call__(self, prefix: str, splitter: str = "/"):
        return self.sub(prefix, splitter)
    

class Argument:
    '''The class that describe an argument.
    
    ### Properties
        - name: the name of the argument.
        - type: how to convert string to a value.
        - default: the value set to the argument if it is not provided.
        - present: the value set to the argument if it is provided but without a value.
        - help: help string.
        - pre_condition: Before an argument is parsed, the pre-condition must be satisfied.
        - post_condition: After an argument is parsed, if the post-condition is not satisfied, then will raise an error. 
    '''
    def __init__(self, 
            name: str, 
            type: Callable[[str] , Any], 
            default: Any = None, 
            present: Any = None,
            help:str = "" , 
            pre_condition : Condition = Condition(), 
            post_condition: Condition = Condition(), 
        ):
        self.name = name
        self.type = type
        self.default = default
        self.present = present
        self.pre_condition  = pre_condition
        self.post_condition = post_condition
        self.help = help

class ArgumentParser:
    '''This class is a modification of python `argparse.ArgumentParser` class.

    For each argument, there are two conditions: pre-condition and post-condition.
    Before an argument is parsed, the pre-condition must be satisfied. 
    After an argument is parsed, if the post-condition is not satisfied, then will raise an error.
    '''

    def __init__(self, help: str = ""):

        self.help = help

        self.arguments: dict[str, Argument] = {}
        self.alias    : dict[str, str] = {} # redirects to

    @property
    def now_preconds(self):
        return [c for id,c in condition_env.items() if c is not None]
    
    @classmethod
    def get_subconfig(cls, C: dict | Namespace, prefix: str, splitter: str = "/"):
        if isinstance(C, Namespace):
            C = C.__dict__
        return get_subdict(C,prefix,splitter)

    def set_arg(self, name: str, key: str, val: Any):
        '''set properties of an argument'''
        arg = self.arguments.get(name)
        if arg is not None:
            arg.__dict__[key] = val

    def add_alias(self, alias: str, original: str):
        '''add an alias for an argument.'''
        self.alias[alias] = original
        
    def add_argument(self, 
        name: str, 
        type: Callable[[str] , Any], 
        default: Any = None, 
        present: Any = None, 
        help: str = "" , 
        verify : Callable[ [Any] , bool] = lambda _: True ,
        aliases: list[str] = [] , 
    ):
        post_cond = Condition(lambda C: verify(C.get(name)))
        self.arguments[name] = Argument(name, type, default, present, help, Condition.and_all(self.now_preconds), post_cond)
        for alias in aliases:
            self.add_alias(alias, name)

    def add_bool(self, 
        name: str, 
        help: str = "" , 
        verify : Callable[[ Any ], bool] = lambda _: True ,
        aliases: list[str] = [] , 
    ):
        self.add_argument(name, bool, False, True, help, verify, aliases)

    def parse_namespace(self, 
            args: list[str] | None = None, 
            pattern = r"^--([^=]+)(=(.+)|)$", 
            get_match: Callable[[re.Match], tuple[str,str]] = lambda m: (m.group(1), m.group(3)) , 
        ) -> Namespace:
            return Namespace(**self.parse(args, pattern, get_match))
    
    def parse(self, 
            args: list[str] | None = None, 
            pattern = r"^--([^=]+)(=(.+)|)$", 
            get_match: Callable[[re.Match], tuple[str,str]] = lambda m: (m.group(1), m.group(3)) , 
        ) -> MyDict:
        ''' Parse argument.

        ### Parameters
            -- args: arguments to be parsed.
            -- pattern: a regular expression to match name and value.
            -- get_match: a callable object that get name and value from the get_match. The input callable is a `re.Match` object, 
                the output should be a 2-tuple, with the first element being the name and the second element being the value of the argument.
        '''
        if args is None:
            args = sys.argv[1:]

        # get value of each argument 
        name_vals = {}            
        for s in args:
            # get name val pairs
            match = re.match(pattern, s)
            if match is None:
                continue
            name, val = get_match(match)

            # apply alias 
            alias_tar = self.alias.get(name)
            if alias_tar is not None:
                name = alias_tar
            
            # apply present val
            arg = self.arguments.get(name)
            if arg is None:
                continue
            if val is None:
                val = arg.present

            # record name, val pair
            name_vals[name] = arg.type(val)
        
        # apply default val
        for name , arg in self.arguments.items():
            if not (name in name_vals):
                name_vals[name] = arg.default

        # actually assign values 
        parsed = {}
        _t = 0
        for _t in range(100):
            now_len = len(parsed)
            for name, val in name_vals.items():

                # get Argument object
                arg = self.arguments.get(name)
                if arg is None:
                    continue
                     
                # check pre condition
                if not arg.pre_condition.test(parsed):
                    continue
                
                # store value
                parsed[name] = val

                # check post condition
                if not arg.post_condition.test(parsed):
                    raise RuntimeError(f"bad argument {name}: value can not be {parsed[name]}")

            new_len = len(parsed)
            if new_len == now_len: # no new argument is parsed
                break
            now_len = new_len

            # update all alias into the parsed
            for alias, name in self.alias.items():
                if name in parsed:
                    parsed[alias] = parsed[name]


        if _t >= 98:
            warnings.warn("Too deep nested logic. Only performed 100 iterations.")
        
        # for those who forbidded by precondition, assign `None`.
        for name in self.arguments:
            if not (name in parsed):
                parsed[name] = None 

        # update all alias into the parsed
        for alias, name in self.alias.items():
            if name in parsed:
                parsed[alias] = parsed[name]

        return MyDict(parsed)


