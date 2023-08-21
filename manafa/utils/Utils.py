import os
from subprocess import Popen, PIPE
import fnmatch


def find_files_with_pattern(basedir, pattern, context=None, only_files=False, only_dirs=False):
    matches = []
    for root, dirs, files in os.walk(basedir):
        if only_files and only_dirs:
            break
        for name in files + dirs:
            full_path = os.path.join(root, name)
            if fnmatch.fnmatch(name, pattern):
                if only_files and os.path.isfile(full_path):
                    matches.append(full_path)
                elif only_dirs and os.path.isdir(full_path):
                    matches.append(full_path)
                elif not only_files and not only_dirs:
                    matches.append(full_path)
    if context:
        matches = [match.format(**context) for match in matches]

    return matches


def get_reference_dir(packname):
        base_dir = os.path.dirname(os.path.dirname(os.path.dirname(__file__)))
        #base_dir = sysconfig.get_path("purelib")
        return os.path.join(base_dir, packname)


def get_resources_dir(packname="manafa", default_res_dir="resources"):
    ref_dir = get_reference_dir(packname)
    return os.path.join(ref_dir, default_res_dir)


def get_test_resources_dir(packname="manafa", default_res_dir="resources"):
    ref_dir = get_reference_dir(packname)
    return os.path.join(ref_dir, 'tests', default_res_dir)


def get_pack_dir(packname="manafa"):
    return get_reference_dir(packname)


def get_results_dir(packname="manafa", default_results_dir="results"):
    ref_dir = get_reference_dir(packname)
    return os.path.join(ref_dir, default_results_dir)


def execute_shell_command(cmd, args=[]):
    command = cmd + " " + " ".join(args) if len(args) > 0 else cmd
    proc = Popen(command, stdout=PIPE, stderr=PIPE, shell=True)
    out, err = proc.communicate()
    return proc.returncode, out.decode("utf-8"), err.decode('utf-8')


def mega_find(basedir, pattern="*", maxdepth=999, mindepth=0, type_file='n'):
    basedir_len = len(basedir.split(os.sep))
    res = find_files_with_pattern(basedir, pattern=pattern, only_files=type_file == 'f', only_dirs=type_file == 'd')
    # filter by depth
    return list(filter(lambda x: basedir_len + mindepth <= len(x.split(os.sep)) <= maxdepth + basedir_len, res))


def is_float(string):
    try:
        float(string)
    except ValueError:
        return False
    return True