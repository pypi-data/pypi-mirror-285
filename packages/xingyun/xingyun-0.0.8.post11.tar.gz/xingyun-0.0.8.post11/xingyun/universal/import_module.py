from importlib import import_module as impo
from types import ModuleType
import warnings 


def my_import_module(module_name: str) -> ModuleType | None:
    try:
        lib = impo(module_name)
    except:
        warnings.warn(f"module {module_name} does not exists.")
        return None

    return lib