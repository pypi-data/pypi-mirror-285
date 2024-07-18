# -*- coding: utf-8 -*-
"""
Created on Sat Oct 23 04:36:47 2019

@author: tommy
"""

import os
import logging

LOGGER_NAME = 'Theo'
DATE_FORMAT = '%Y-%m-%d %H:%M:%S'
CONSOLE_FORMAT = '[%(levelname)1.1s %(asctime)s] %(message)s'
FILE_FORMAT = '[%(levelname)1.1s %(asctime)s %(module)s:%(lineno)d] %(message)s'
LOG_LEVELS = {'debug': logging.DEBUG, #10
              'info': logging.INFO, #20
              'warn': logging.WARNING, #30
              'warning': logging.WARNING, #30
              'error': logging.ERROR, #40
              'critical': logging.CRITICAL} #50
ERR = f'Invalid arg for {0}_level. valid levels are: {list(LOG_LEVELS.keys())}'

def _create_logger(file=None, file_level='info', console_level='debug'):
    
    logger = logging.getLogger(LOGGER_NAME)
    logger.file, logger.file_level, = file, file_level
    logger.console_level, logger.propagate = console_level, False
    logger.setLevel(logging.DEBUG)
    
    logger.close = close.__get__(logger)
    logger.reset = reset.__get__(logger)
    
    logger.d = d.__get__(logger)
    logger.i = i.__get__(logger)
    logger.w = w.__get__(logger)
    logger.e = e.__get__(logger)
    logger.c = c.__get__(logger)
    logger.warn = warn.__get__(logger)
    
    logger = logger.reset(file, file_level, console_level)
    
    return logger

def close(self):
    '''
    removes all log handlers from logger object
    '''
    for handler in list(self.handlers):
        handler.close()
        self.removeHandler(handler)

def reset(self, file=None, file_level='info', console_level='debug', 
          remove_file=False):
    '''
    modifies logger obeject behavior

    Parameters
    ----------
    file : str, optional
        file path to save log messages to. 
        The default is None and will not ouput logs to a file.
    file_level : str, optional
        logging level for logs sent to a file. The default is 'info'. level
        must be one of: debug, info, warn, error or critical
    console_level : str, optional
        logging level for logs sent to a console / std out. The default is 
        'debug'. level must be one of: debug, info, warn, error or critical
    remove_file : boolena, optional
        delete the log file before creating a new one. The default is False.

    Returns
    -------
    modified logging.Logger object
    '''

    assert console_level in LOG_LEVELS.keys(), ERR.replace('0', 'console')
    if file:
        assert file_level in LOG_LEVELS.keys(), ERR.replace('0', 'file')
    
    self.close()
    self.file = file 
    self.file_level = file_level 
    self.console_level = console_level 
    self.setLevel(logging.DEBUG)

    c_fmt = logging.Formatter(CONSOLE_FORMAT, datefmt = DATE_FORMAT)
    f_fmt = logging.Formatter(FILE_FORMAT, datefmt = DATE_FORMAT)
    
    ch = logging.StreamHandler()
    ch.setLevel(LOG_LEVELS[self.console_level])
    ch.setFormatter(c_fmt)
    self.addHandler(ch)
    
    if remove_file and file is not None:
        if os.path.exists(file):
            os.remove(file)
    
    if self.file:
        fh = logging.FileHandler(self.file)
        fh.setLevel(LOG_LEVELS[self.file_level])
        fh.setFormatter(f_fmt)
        self.addHandler(fh)
    
    return self # for usage consistency    

def d(self, msg, *args, **kwargs):
    if self.isEnabledFor(logging.DEBUG):
        self._log(logging.DEBUG, msg, args, **kwargs)
def i(self, msg, *args, **kwargs):
    if self.isEnabledFor(logging.INFO):
        self._log(logging.INFO, msg, args, **kwargs)
def w(self, msg, *args, **kwargs):
    if self.isEnabledFor(logging.WARNING):
        self._log(logging.WARNING, msg, args, **kwargs)
def e(self, msg, *args, **kwargs):
    if self.isEnabledFor(logging.ERROR):
        self._log(logging.ERROR, msg, args, **kwargs)
def c(self, msg, *args, **kwargs):
    if self.isEnabledFor(logging.CRITICAL):
        self._log(logging.CRITICAL, msg, args, **kwargs)     
def warn(self, msg, *args, **kwargs):
    if self.isEnabledFor(logging.WARNING):
        self._log(logging.WARNING, msg, args, **kwargs)

logger = _create_logger()
log, lg = logger, logger
