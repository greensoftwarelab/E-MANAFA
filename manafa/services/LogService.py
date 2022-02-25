import time,sys, os


from .service import Service

import re
from ..utils.Utils import execute_shell_command
from manafa.utils.Logger import log


class LogService(Service):
    def __init__(self, boot_time=0, output_res_folder="hunter"):
        Service.__init__(self, output_res_folder)
        self.trace = {}
        self.boot_time = boot_time
        self.end_time = boot_time

    def config(self, **kwargs):
        pass

    def init(self, boot_time=0, **kwargs):
        self.boot_time = boot_time
        self.trace = {}

    def start(self, run_id=None):
        self.clean()

    def get_results_filename(self, run_id):
        if run_id is None:
            run_id = execute_shell_command("date +%s")[1].strip()
        return os.path.join(self.results_dir, "hunter-%s-%s.log" % (run_id, str(self.boot_time)))

    def stop(self, run_id=None):
        filename = self.get_results_filename(run_id)
        time.sleep(1)
        execute_shell_command("adb logcat -d | grep -io \"[<>].*m=example.*]\" > %s" % filename)
        return filename

    def clean(self):
        execute_shell_command("find %s -type f  | xargs rm " % self.results_dir)
        execute_shell_command("adb logcat -c")  # or   adb logcat -b all -c
