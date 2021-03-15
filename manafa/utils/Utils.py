from subprocess import Popen, PIPE
from textops import find

def execute_shell_command(cmd, args=[]):
    command = cmd + " " + " ".join(args) if len(args) > 0 else cmd
    proc = Popen(command, stdout=PIPE, stderr=PIPE,shell=True)
    out, err = proc.communicate()
    return proc.returncode, out.decode("utf-8") , err.decode('utf-8')

def mega_find(basedir, pattern="*", maxdepth=999, mindepth=0, type_file='n'):
    basedir_len = len(basedir.split("/"))
    res = find(basedir, pattern=pattern, only_files=type_file=='f',only_dirs=type_file=='d' )
    # filter by depth
    return list( filter(lambda x : len(x.split("/")) >= basedir_len + mindepth and len(x.split("/")) <= maxdepth + basedir_len , res ) )