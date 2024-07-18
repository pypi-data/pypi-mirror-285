# -*- coding: utf-8 -*-
"""
Created on Sat Oct 23 04:36:47 2019

Easy logging, timing and email notifications of code execution.

@author: tommy
"""

from .__logger import logger, log, lg
from .notify import notify
from .dirty_timer import beg, end, timer
from .sys_meta import (
    get_cpu_model,
    get_machine_info,
    get_resource_usage,
    get_imported_pkg_vers,
    get_env_info,
    sys_info
    )

from .__ver import __version__

try:
    del __ver, __logger
except:
    pass 