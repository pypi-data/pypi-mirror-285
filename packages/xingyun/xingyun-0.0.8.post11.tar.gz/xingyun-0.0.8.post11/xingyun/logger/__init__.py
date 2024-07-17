'''This module provides methods to manage and save data.'''

from .base import DataAccess, get_aws3_dataacess, get_dropbox_dataacess
from .getid import get_id
from .globaldata import GlobalDataManager, make_hook_logger, HookType
from .logger import Logger
