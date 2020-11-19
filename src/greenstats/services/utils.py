

import shutil
import subprocess

really_execute=True

def executeShCommand(command):
    if not really_execute:
        print(command)
        return 0
    pipes = subprocess.Popen(command, stdout=subprocess.PIPE, stderr=subprocess.PIPE, shell=True)
    std_out, std_err = pipes.communicate()
    output = std_out.decode("utf-8").lower()
    if pipes.returncode != 0:
        err_msg = "%s. Code: %s" % (std_err.decode('utf-8').strip(), pipes.returncode)
        print("error executing command %s" % command)
        print(err_msg)
        return -1    
    elif len(std_err)==0:
        return output
