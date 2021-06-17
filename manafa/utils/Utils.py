import os
from subprocess import Popen, PIPE
from textops import find

def get_reference_dir(packname):
        base_dir = os.path.dirname(os.path.dirname(os.path.dirname(__file__)))
        #base_dir = sysconfig.get_path("purelib")
        return os.path.join(base_dir, packname)

def get_resources_dir(packname="manafa", default_res_dir="resources"):
    ref_dir = get_reference_dir(packname)
    return os.path.join(ref_dir, default_res_dir)


def get_pack_dir(packname="manafa"):
    return get_reference_dir(packname)


def get_results_dir(packname="manafa", default_results_dir="results"):
    ref_dir = get_reference_dir(packname)
    return os.path.join(ref_dir, default_results_dir)


def execute_shell_command(cmd, args=[]):
    command = cmd + " " + " ".join(args) if len(args) > 0 else cmd
    proc = Popen(command, stdout=PIPE, stderr=PIPE,shell=True)
    out, err = proc.communicate()
    return proc.returncode, out.decode("utf-8") , err.decode('utf-8')

def mega_find(basedir, pattern="*", maxdepth=999, mindepth=0, type_file='n'):
    basedir_len = len(basedir.split("/"))
    res = find(basedir, pattern=pattern, only_files=type_file=='f', only_dirs=type_file=='d' )
    # filter by depth
    return list( filter(lambda x : len(x.split("/")) >= basedir_len + mindepth and len(x.split("/")) <= maxdepth + basedir_len , res ) )

def is_float(string):
    try:
        float(string)
    except ValueError:
        return False
    return True