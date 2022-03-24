import time, os, json

from textops import cat

from manafa.services.service import Service

import re
from manafa.utils.Utils import execute_shell_command, get_results_dir
from manafa.utils.Logger import log

RESULTS_DIR = get_results_dir()


class AppConsumptionStats(object):
    """Class that stores method traces of apps registered with hunter.

        This class parses and batterystats history events from files parsed using parseFile function. It starts by load
        information contained in the device power profile file and also the current state values known by the profiler,
        stored in definitions attribute.

        Attributes:
            app_traces (dict): method traces.
            results_dir (int): results' directory.
        """
    def __init__(self, results_dir=os.path.join(RESULTS_DIR, "consumptions")):
        self.results_dir = results_dir
        if not os.path.exists(self.results_dir):
            os.mkdir(self.results_dir)
        self.app_traces = {}
        
    def clean(self):
        """clears app_traces attribute.
        """
        self.app_traces.clear()

    def get_output_filepath(self, test_id):
        """gets path of output file where the consumption info will be written.
        Returns:
            str: filepath
        """
        filename = f"consumptions-{test_id}.log"
        return os.path.join(self.results_dir, filename)

    @staticmethod
    def write_consumptions(filename, consumption, function=None):
        """writes consumption info to file.
        Args:
            filename(str): path of output file.
            consumption(float): consumption value.
            function: option function name if the consumption is from a function.
        """
        if function is not None:
            line = "%s : %f Joules\n" % (function, consumption)
        else:
            line = "\nTOTAL: %f Joules" % consumption

        with open(filename, 'a') as filehandle:
            filehandle.write(line)

        filehandle.close()
    
    def save_function_info(self, filename, filter_zeros=False):
        """save method traces contained in app_traces to file.
        Args:
            filename: name of output file.
            filter_zeros: filter zeros
        Returns:
            str: path of the output file
        """
        filepath = os.path.join(self.results_dir, filename)
        with open(filepath, 'w') as jj:
            json.dump(self.app_traces, jj, indent=1)
        return filepath
