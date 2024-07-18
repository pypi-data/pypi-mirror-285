# -*- coding: utf-8 -*-
"""
Created on Fri Oct 15 07:15:17 2021
@author: tommy
"""

#%% libs

import re
import time
import smtplib
import traceback
import pandas as pd
from tabulate import tabulate
from datetime import timedelta
from email.mime.text import MIMEText
from inspect import signature, getfullargspec
from email.mime.multipart import MIMEMultipart

try:
    from icecream import ic
except ImportError:  # Graceful fallback if IceCream isn't installed.
    ic = lambda *a: None if not a else (a[0] if len(a) == 1 else a)  

#%% exec_func

def _exec_func(function, email, timeit, logger, printf, notes, error, host, 
               stacklvl, *args, **kwargs):
    
    code, fn_name = _parse_stack(function, stacklvl)
    exec_times, latest_error, err_traceback = [], None, None
    
    for i in range(1,timeit+1):
        _log_msg(logger, printf, f"Starting: {code}...")
        if notes and i == 1:
            _log_msg(logger, printf, f"Notes: {notes}")
        try:
            t1, start_time = time.perf_counter(), pd.to_datetime('today') 
            result = function(*args, **kwargs)
        except Exception as err:
            latest_error = err
            err_traceback = traceback.format_exc() 
        _log_msg(logger, printf, f"Finished: {code}...")
        exec_times.append(time.perf_counter() - t1)
        end_time = pd.to_datetime('today')
    min_exec_tm = str(timedelta(seconds = min(exec_times))).rstrip('0')
    result = result if latest_error is None else latest_error

    fn_meta = _fn_meta(function, args, kwargs, result)
    _log_msg(logger, printf, _format_msg(fn_meta, fn_name, min_exec_tm))
    _send_email(email, host, fn_meta, fn_name, latest_error, min_exec_tm, code, 
                start_time, end_time, err_traceback, notes)
        
    if latest_error is not None:
        _log_msg(logger, printf, f"Error in: {code}...\n{err_traceback}", 
                 err_traceback)
        if error:
            raise latest_error
    
    return result

#%% helpers 

def _parse_stack(function, stacklvl):
    
    fn_name = function.__name__
    stack = traceback.extract_stack()
    
    if stacklvl:
        _, _, _, code = stack[stacklvl] 
        return code, fn_name
    
    for lvl in range(-4,-13,-1):
        _, _, _, code = stack[lvl] 
        if fn_name in code:
            break
        
    if fn_name not in code:
        raise ValueError('Unable to guess the stack trace level that contains'\
                         ' the correct function call. Ensure notify is used'\
                         ' as the first decorator.')
            
    return code, fn_name

def _parse_fn_signature(function):
    fn_signature = str(signature(function))
    params = re.findall(r'([^\s|^,|^\(|^\)]+)', fn_signature)
    params = [re.sub(r'=.+', '', f) for f in params]
    
    #TODO: this is same thing?
    argspec = getfullargspec(function)
    params = argspec.args
    
    return params
               
def _log_msg(logger, printf, msg, err_traceback = None):
        
    if logger is not None:
        if err_traceback is None:
            logger.info(msg, stacklevel=4) # for stack frame of org caller
        else:
            logger.error(msg, stacklevel=4)
            
    if printf:
        print(f"{pd.to_datetime('today').strftime('[%y%m%d %H:%M:%S]')} {msg}")

def _custom_obj_str(obj):
    if hasattr(obj, 'columns'):
        cols = [str(col) for col in obj.columns]
        strg = f"cols: {', '.join(cols)}"
        strg = strg[0:50] + '...' if len(strg) > 50 else strg
    elif hasattr(obj, '__str__'):
        strg = str(obj)
        strg = strg if len(strg) <= 50 else 'NA'
    else:
        strg = 'NA'
    return strg

def _len(obj):
    if hasattr(obj, 'shape'):
            length = obj.shape
    elif hasattr(obj, '__len__'):
        length = len(obj)
    else:
        length = 'NA'
    return length

def _fn_meta(function, args, kwargs, result):
    params = getfullargspec(function).args
    all_args = dict(zip(params[0:len(args)], args))
    all_args.update(kwargs)
    all_args.update({'output': result})
    
    meta = []
    for param, arg in all_args.items():
        type_ = re.sub('<class |>', '', str(type(arg)))
        split_type = type_.split('.')
        if len(split_type) > 1:
            type_ = f"{split_type[0]}.{split_type[-1]}"
        meta.append([param, type_, _len(arg), _custom_obj_str(arg)])
        
    cols = ['Variable', 'Type', 'Length', 'String']
    meta = pd.DataFrame.from_records(meta, columns = cols) 
    
    return meta

def _email_inputs(fn_meta, fn_name, latest_error, min_exec_tm,
                  code, start_time, end_time, err_traceback, notes):
    
    status = 'Successfully' if latest_error is None else 'w/ Errors'
    subject = f'TheLogger: {fn_name} Executed {status} ({min_exec_tm})'
    

    if latest_error is not None:
        err_tb = err_traceback.replace('\n', '<br>')
        err_tb = err_tb.replace('Traceback (most recent call last):',
                         '<b>Exception Traceback (most recent call last):</b>')
        err_tb = f'{err_tb}<br>'
        
    else:
        err_tb = ''
        
    body = f"""\
    <html>
      <head></head>
      <body>
        <p><b>Executed:</b> {code}...<br><br>
           :notes
           <b>Start Time:</b> {start_time}<br>
           <b>End Time:</b> {end_time}<br>
           <b>Elasped Time:</b> {min_exec_tm}<br><br>
           <b>Input(s) and Output of <i>{fn_name}</i>:</b>
           {fn_meta.to_html(index = False)}<br>
           {err_tb}
           --<br>
           <b>See The Docs:</b> <a href="https://www.python.org/">TheLogger</a> 
        </p>
      </body>
    </html>
    """
    
    notes_html = f"<b>Notes:</b> {notes}...<br><br>" if notes else ''
    body = body.replace(':notes', notes_html)
        
    return  subject, body

def _send_email(email, host, fn_meta, fn_name, latest_error, min_exec_tm, code, 
                start_time, end_time, err_traceback, notes):
    
    if email is None:
        return None
    
    subject, body = _email_inputs(fn_meta, fn_name, latest_error, min_exec_tm,
                                  code, start_time, end_time, err_traceback, notes)
    
    emsg = MIMEMultipart()
    if host is None:
        s = smtplib.SMTP(host='smtp.gmail.com', port=587)
        s.starttls() 
        s.login('py.notify1@gmail.com', 'ytbxunbpmabkvmhn')
        emsg['From'] = 'py.notify1@gmail.com' 
    else:
        s = smtplib.SMTP(host=host)
        emsg['From'] = email        
        
    emsg['To'] = email
    emsg['Subject'] = subject
    emsg.attach(MIMEText(body, 'html'))
    s.send_message(emsg)
    s.quit()

def _format_msg(fn_meta, fn_name, min_exec_tm):
    fn_meta_txt = tabulate(fn_meta, tablefmt="psql", numalign = 'left',
                           headers = fn_meta.columns, showindex = False)
    msg = f"Input(s) / Output of {fn_name}:\n{fn_meta_txt}"
    msg = f"{msg}\nElapsed Time: {min_exec_tm}"
    return msg