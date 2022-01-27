import time, os, json

from textops import cat

from manafa.services.service import Service

import re
from ..utils.Utils import execute_shell_command, get_results_dir
from manafa.utils.Logger import log

RESULTS_DIR = get_results_dir()


class AppConsumptionStats(object):
    def __init__(self, results_dir=os.path.join(RESULTS_DIR, "consumptions")):
        self.results_dir = results_dir
        self.app_traces = {}
        
    def clean(self):
        self.method_traces.clear()

    def get_output_filepath(self, test_id):
        filename = f"consumptions-{test_id}.log" 
        return os.path.join(self.results_dir, filename)

    def write_consumptions(self, filename, consumption, function=None):
        if function is not None:
            line = "%s : %f Joules\n" % (function, consumption)
        else:
            line = "\nTOTAL: %f Joules" % consumption

        with open(filename, 'a') as filehandle:
            filehandle.write(line)

        filehandle.close()
    
    def save_function_info(self, filename, filter_zeros=False):
        filepath = os.path.join(self.results_dir, filename)
        with open(filepath, 'w') as jj:
            json.dump(self.app_traces, jj, indent=1)
        return filepath
