import time

from textops import cat

from .service import Service

import re
from ..utils.Utils import execute_shell_command
from manafa.utils.Logger import log


class AppConsumptionsService(Service):
    def __init__(self, boot_time=0, output_res_folder="consumptions"):
        Service.__init__(self, output_res_folder)
        self.boot_time = boot_time

    def config(self, **kwargs):
        pass

    def init(self, boot_time=0, **kwargs):
        self.boot_time = boot_time

    def start(self, run_id=None):
        self.clean()

    def stop(self, run_id=None):
        if run_id is None:
            run_id = execute_shell_command("date +%s")[1].strip()
        filename = self.results_dir + "/consumptions-%s-%s.log" % (run_id, str(self.boot_time))
        return filename

    def clean(self):
        execute_shell_command("find %s -type f  | xargs rm " % self.results_dir)

    def write_consumptions(self, filename, consumption, function=None):
        if function is not None:
            line = "%s : %f Joules\n" % (function, consumption)
        else:
            line = "\nTOTAL: %f Joules\n" % consumption

        with open(filename, 'a') as filehandle:
            filehandle.write(line)

        filehandle.close()
