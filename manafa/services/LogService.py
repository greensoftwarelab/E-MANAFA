import time,sys, os


from .service import Service

import re
from ..utils.Utils import execute_shell_command
from manafa.utils.Logger import log


class LogService(Service):
    """Class that manages the device's log.

    This class is responsible by cleaning the log before each execution of the framework, as well as dump the log
     right after each execution.

    Attributes:
        boot_time (float): timestamp of the device's last boot.
        output_res_folder (float): folder where the logs will be stored after each profiling session.
    """
    def __init__(self, boot_time=0, output_res_folder="hunter"):
        Service.__init__(self, output_res_folder)
        self.trace = {}
        self.boot_time = boot_time
        self.end_time = boot_time

    def config(self, **kwargs):
        pass

    def init(self, boot_time=0, **kwargs):
        """inits the class.
        Args:
            boot_time: device boot timestamp.
            **kwargs:
        """
        self.boot_time = boot_time
        self.trace = {}


    def start(self, run_id=None):
        """starts the profiling session.

        Calls clean() to discard logs prior to the start of the session.
        Args:
            run_id(str): current session/run id.  Considered only for API compat purposes.
        """
        self.clean()

    def get_results_filename(self, run_id):
        """returns the name of the output file.
        Returns:
            output_name: the name of the output file.
        """
        if run_id is None:
            run_id = execute_shell_command("date +%s")[1].strip()
        return os.path.join(self.results_dir, "hunter-%s-%s.log" % (run_id, str(self.boot_time)))

    def stop(self, run_id=None):
        """stops the profiling session.

        Dump the logs in output file.
        Returns:
            filename: the name of the output file.
        """
        filename = self.get_results_filename(run_id)
        time.sleep(1)
        execute_shell_command("adb logcat -d | grep -E '(<|>).*_.*\[[0-9]+' | cut -f4 -d\: | tr -d ' ' > %s" % filename)
        #execute_shell_command("adb logcat -d | grep -io \"[<>].*m=example.*]\" > %s" % filename)
        return filename

    def clean(self):
        """cleans device log state and removes files from previous runs.
        """
        execute_shell_command("find %s -type f  | xargs rm " % self.results_dir)
        execute_shell_command("adb logcat -c")  # or   adb logcat -b all -c
