import time,sys, os


from .service import Service

import re
from ..utils.Utils import execute_shell_command
from manafa.utils.Logger import log

DEVICE_RESULTS_DIR = "/data/local/tmp/"
TRACE_PROCESSOR_PATH = "~/repos/research/perfetto/tools/trace_processor"

def convert_to_csv(file_to_convert, results_dir=None):
    #  ~/repos/research/perfetto/tools/trace_processor xisco -Q "SELECT name, ts, dur, depth FROM slice ORDER BY ts"
    results_dir = results_dir if results_dir is not None else os.path.dirname(file_to_convert)
    filepath = file_to_convert.replace(".trace", ".csv")
    target_file = os.path.join(results_dir, os.path.basename(filepath))
    cmd = f"{TRACE_PROCESSOR_PATH} {os.path.join(results_dir, file_to_convert)} -Q \"SELECT name, ts, dur, depth FROM slice ORDER BY ts\" > {target_file}"
    log("Converting %s to CSV: " % cmd)
    res = execute_shell_command(cmd)
    #print(res)
    return target_file


class AmProfilerService(Service):
    """Class that manages the am profiler.

    This class is responsible by managing the Android Activity Manager (am) profiler, which is used to collect
    method execution traces from the Android system and applications

    Attributes:
        boot_time (float): timestamp of the device's last boot.
        output_res_folder (float): folder where the logs will be stored after each profiling session.
    """
    def __init__(self, package_name, boot_time=0, output_res_folder="am"):
        Service.__init__(self, output_res_folder)
        self.trace = {}
        self.package_name = package_name
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
        #self.clean()
        output_filename = self.get_results_filename(run_id)
        log("Am Profiler run id:  %s" % run_id)
        res = execute_shell_command(" adb shell cmd package resolve-activity --brief %s | grep %s" % (self.package_name, self.package_name))
        activity_package = res[1].strip()
        cmd = " adb shell am start -S -n %s -P %s" % (activity_package, output_filename )
        log("Starting Am Profiler: " + cmd)
        res = execute_shell_command(cmd)
        return res[0] == 0

    def get_results_filename(self, run_id):
        """returns the name of the output file.
        Returns:
            output_name: the name of the output file.
        """
        # something like /data/local/tmp/app.trac
        if run_id is None:
            run_id = execute_shell_command("date +%s")[1].strip()
        return os.path.join(DEVICE_RESULTS_DIR, "app_%s_%s_%s.trace" % (self.package_name, run_id, str(self.boot_time)))

    def stop(self, run_id=None):
        """stops the profiling session.

        Dump the logs in output file.
        Returns:
            filename: the name of the output file.
        """
        log("Stopping Am Profiler for package: %s" % self.package_name)
        execute_shell_command("adb shell am profile stop %s" % self.package_name)
        filename = execute_shell_command("adb shell ls %s | grep app_%s" % (DEVICE_RESULTS_DIR, self.package_name))[1].strip()
        log("Am Profiler file:  %s" % filename)
        res, o, e = execute_shell_command(f"adb pull {DEVICE_RESULTS_DIR}/{filename}  {self.results_dir}")
        if res != 0:
            raise Exception(f"unable to pull trace file. Attempted to pull {filename}")
        exported_filename = self.export()
        log("Exported Am Profiler file:  %s" % exported_filename)
        return exported_filename

    def clean(self):
        """cleans device log state and removes files from previous runs.
        """
        res = execute_shell_command(f"adb shell xargs rm {DEVICE_RESULTS_DIR}/app_*.trace")
        print(res)
        res = execute_shell_command(
            f"find {self.results_dir} -type f -name \"app_*.trace\"  | xargs rm ")

    def export(self):
        """Exports results from previous runs.
            last_exported: path of last exported file.
        """
        log("Exporting Am Profiler results to CSV: %s" % self.results_dir)
        target_file = ""
        for f in filter(lambda x: re.match(r'app_*', x) is not None, os.listdir(self.results_dir)):
            log(f)
            f_file = os.path.join(self.results_dir, f)
            if not os.path.exists(f_file):
                raise Exception(f"trace file not found ({f_file})")
            last_exported = os.path.join(self.results_dir, f)
            log("Converting %s to CSV: " % last_exported)
            target_file = convert_to_csv(f_file, self.results_dir)
        return target_file
