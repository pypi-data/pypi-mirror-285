import random
import time
from typing import Literal, TypeAlias, NoReturn, List
from xingyun.universal.import_module import my_import_module

'''literals that are allowed in the `module` parameter.'''
RandomAllowedModule: TypeAlias = Literal["torch"] | Literal["numpy"] | Literal["random"] 

def set_module_seed(seed: int , module: RandomAllowedModule):
    '''set random seed of a specific module.'''
    
    if module == "torch":
        torch = my_import_module("torch")
        cuda  = my_import_module("torch.cuda")

        if (torch is None) or (cuda is None):
            return 
        
        torch.manual_seed(seed)

        cuda.manual_seed_all(seed)

        backends = my_import_module("torch.backends")
        backends.cudnn.deterministic = True
        backends.cudnn.benchmark = False

    if module == "numpy":
        np = my_import_module("numpy")

        if np is None:
            return 
        
        np.random.seed(seed)
        
    if module == "random":
        random.seed(seed)


def set_random_seed(seed: int , modules: List[RandomAllowedModule] = ["random" , "torch" , "numpy"]):
    '''Set random seed.
        
    ### Parameters
        - seed: random seed.
        - modules: Which module to set. Support `random`, `torch` and `numpy`.
            Notice that the random seed of `torch.cuda` will also be set.
    '''
    [set_module_seed(seed, m) for m in modules]
