"""
Quick and dirty utilties for timing code.
"""

import os
import time
import contextlib
from datetime import timedelta

def beg():
    beg_tm = time.perf_counter()
    os.environ['the_logger_time'] =  str(beg_tm)

def end():
    end_tm = time.perf_counter()
    beg_tm = float(os.environ['the_logger_time'])
    sec_delta = end_tm - beg_tm
    sec_delta = round(sec_delta, 3)
    exec_tm = str(timedelta(seconds = sec_delta)).rstrip('0')
    print(f"Elapsed Time: {exec_tm}")
    
@contextlib.contextmanager 
def timer():
    """
    Context manager that provides timing of code execution.

    Example
    -------
    >>> import thelogger as tl
    >>> import time 
    >>> with tl.timer():
    ...     time.sleep(1)
    Elapsed Time: 0:00:00.999
    """
    beg_tm = time.perf_counter()
    yield 
    end_tm = time.perf_counter()
    sec_delta = end_tm - beg_tm
    sec_delta = round(sec_delta, 3)
    exec_tm = str(timedelta(seconds = sec_delta)).rstrip('0')
    print(f"Elapsed Time: {exec_tm}")
    