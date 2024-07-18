# -*- coding: utf-8 -*-
"""
Created on Fri Oct 15 07:15:17 2021

@author: tommy
"""

from functools import wraps, partial
from .exec_func import _exec_func

def notify(function=None, *, email=None, timeit=1, logger=None, printf=None,
           notes=None, error=True, host=None, stacklvl=None, setdefault=False, 
           test=False):
    '''
    Decorator that sends an email with execution details of a function. This 
    must be first decorator of a function for the function details logged to be 
    relevant, otherwise it will log details of subsequent decorators.

    Parameters
    ----------
    function : function
        the function that is decorated
    * : 
        syntax to prevent passing non keyword args.
    email : str, optional
        email address for receiving function execution details. The default is 
        None and no email will be sent
    timeit : int, optional
        number of times to run the function. Used for getting a more accurate
        timing of function execution time. The default is 1.
    logger : logging.Logger object. when passed the execution details are 
        logged using the logger, optional. The default is None.
    printf : boolean, optional
        If True then the execution details are printed to the console. The 
        default is None and will print to console.
    notes : str, optional
        text that's included in the email and log. The default is None.
    error : boolean, optional
        if False then errors produced by the function are caught, logged but 
        not raised. The default is True.
    host : str, optional
        remote host that email is sent thru. if sending emails thru gmail is 
        blocked by your organization then a valid host must be passed 
        The default is None. (e.g. 'mail.abc.com')
    stacklvl : int, optional
        stack trace level used to log function execution details. By default it 
        will guess -4 and decrease the level down to -12 until the correct 
        level is found. 
    setdefault : boolean, optional
        if true then a version of the notify function is returned with given 
        args set as the default. The default is False. 
        (e.g. notify = notify(email = 'myemail@mail.com', setdefault = True))
    test : boolean, optional
        if true then notify is executed with dummy function for testing. 
        The default is False. 
        (e.g. notify(email='myemail.mail.com', test= True))

    Returns
    -------
    whatever the input function returns

    '''
    printf = True if printf is None and logger is None else printf
    printf = False if printf is None and logger is not None else printf
    if test:
        def test_func():
            return "Pass"
        function = test_func
        stacklvl = -5
    if setdefault:
        return partial(notify, email=email, timeit=timeit, logger=logger, 
                       printf=printf, notes=notes, error=error, host=host,
                       stacklvl=stacklvl)
    if function is None: # if @notifiy is used w/ args passed, return decorator
        return partial(notify, email=email, timeit=timeit, logger=logger, 
                       printf=printf, notes=notes, error=error, host=host,
                       stacklvl=stacklvl)
    @wraps(function)
    def wrapper(*args, **kwargs):
        return _exec_func(function, email, timeit, logger, printf, notes,  
                          error, host, stacklvl, *args, **kwargs)
    if test:
        return wrapper()
    return wrapper
