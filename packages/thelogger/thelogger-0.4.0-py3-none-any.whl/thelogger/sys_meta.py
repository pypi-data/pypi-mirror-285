import sys
import pytz
import socket
import psutil 
import datetime
import platform
import subprocess
import pandas as pd
from tzlocal import get_localzone
from importlib.metadata import version

def get_cpu_model():
    if platform.system() == 'Windows':
        try:
            command = 'wmic cpu get name /value'
            output = subprocess.check_output(command, shell=True, 
                                             universal_newlines=True)
            cpu_model = output.strip().split('=')[1]
            return cpu_model
        except subprocess.CalledProcessError:
            return "Unknown"
    elif platform.system() == 'Linux':
        try:
            command = "cat /proc/cpuinfo | grep 'model name' | uniq"
            output = subprocess.check_output(command, shell=True, 
                                             universal_newlines=True)
            cpu_model = output.strip().split(':')[1].strip()
            return cpu_model
        except subprocess.CalledProcessError:
            return "Unknown"
    else:
        return "Unknown"
    
def get_machine_info():
    gb = 1024.0 ** 3
    machine_info = dict(
        machine_name = socket.gethostname(),
        machine_timezone = str(get_localzone()),
        operating_system = platform.system(),
        os_version = platform.release(),
        cpu_model = get_cpu_model(),
        cpu_architecture = platform.machine(),
        cpu_cores = psutil.cpu_count(), # includes hyperthreads
        total_memory = round(psutil.virtual_memory().total / gb, 2)
        )
    return machine_info

def get_resource_usage(tz = 'America/New_York'):
    
    utc_now = datetime.datetime.utcnow()
    utc_now = utc_now.replace(tzinfo=pytz.utc)
    tz = pytz.timezone(tz)
    dttm = utc_now.astimezone(tz)
    dttm =  dttm.strftime("%Y-%m-%d %H:%M:%S.%f %Z")
    cpu_used = psutil.cpu_percent()
    memory_used = psutil.virtual_memory().percent 
    usage = dict(
        cpu_used = str(cpu_used) + '%',
        memory_used = str(memory_used)  + '%',
        datetime = dttm
        )
    return usage

def try_version(x):
    # some pkgs have diff dist names so this doesnt always work
    # std libs don't have versions
    try:
        ver = version(x)
    except:
        ver = None
    return ver

def get_imported_pkg_vers():
    nms = []
    vers = []
    sys_modules = sys.modules.copy()
    for module_name, module in sys_modules.items():
        if (module and hasattr(module, '__package__') and module.__package__
        and module_name[0] != '_' and '.' not in module_name):
            try:
                # some pkgs dont have __version__ attr
                ver = getattr(module, '__version__')
            except:
                ver = None 
            nms.append(module.__package__)
            vers.append(ver)
    imp_mod = pd.DataFrame(dict(nm=nms, ver=vers)).drop_duplicates()
    missing_ver = imp_mod.loc[imp_mod.ver.isnull()]
    ver_from_meta = missing_ver.nm.apply(lambda x: try_version(x))
    imp_mod.ver = imp_mod.ver.fillna(ver_from_meta)
    imp_mod.ver = imp_mod.ver.str.strip()
    imp_mod = imp_mod.loc[imp_mod.ver.notnull()].drop_duplicates()\
        .sort_values('nm').reset_index(drop=True)
    imp_mod.columns = ['pkgs', 'version']
            
    return imp_mod

def get_env_info(pkgs = None):
    py_ver = ".".join(str(component) for component in sys.version_info[:3])
    pkgs = [pkgs] if type(pkgs) == str else pkgs
    imported_pkgs = get_imported_pkg_vers()
    if pkgs:
        imported_pkgs = imported_pkgs.loc[imported_pkgs.pkgs.isin(pkgs)] 
    imported_pkgs = imported_pkgs.sort_values('pkgs')
    pkg_ver = dict(zip(imported_pkgs.pkgs, imported_pkgs.version))
    env_info = dict(python_version = py_ver,
                    python_path = sys.executable,
                    package_versions = pkg_ver)
    return env_info
        
def sys_info(pkgs = None, tz = 'America/New_York'):
    # pkgs: str or list to filter for only specific pkgs. pkg must be imported
    machine_info = get_machine_info()
    usage = get_resource_usage(tz)
    env_info = get_env_info(pkgs)
    out = dict(
        system_name = machine_info['machine_name'],
        system_timezone = machine_info['machine_timezone'],
        datetime = usage['datetime'],
        operating_system = machine_info['operating_system'],
        os_version = machine_info['os_version'],
        cpu_model = machine_info['cpu_model'], 
        cpu_architecture = machine_info['cpu_architecture'],
        cpu_cores = machine_info['cpu_cores'],
        cpu_used = usage['cpu_used'],
        total_memory = machine_info['total_memory'],
        memory_used = usage['memory_used']
        )
    out = {**out, **env_info}
    return out
    
