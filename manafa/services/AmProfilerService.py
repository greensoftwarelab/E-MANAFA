import os
import time

from .service import Service
import re
from ..utils.Utils import execute_shell_command, get_resources_dir
from manafa.utils.Logger import log

DEVICE_RESULTS_DIR = "/data/local/tmp/"
TRACE_PROCESSOR_PATH = os.path.join(get_resources_dir() , "trace_processor")
PROFILING_SAMPLE_RATE = 750  # in nanosecs, default sampling rate for am profiler

def convert_to_csv(file_to_convert, results_dir=None):
    #  ~/repos/research/perfetto/tools/trace_processor tracefile -Q "SELECT name, ts, dur, depth FROM slice ORDER BY ts"
    results_dir = results_dir if results_dir is not None else os.path.dirname(file_to_convert)
    filepath = file_to_convert.replace(".trace", ".csv")
    target_file = os.path.join(results_dir, os.path.basename(filepath))
    cmd = f"{TRACE_PROCESSOR_PATH} {os.path.join(results_dir, file_to_convert)} -Q \"SELECT name, ts, dur, depth FROM slice ORDER BY ts\" > {target_file}"
    log("Converting %s to CSV: " % cmd)
    res = execute_shell_command(cmd)
    corresp_exec_file = file_to_convert.replace(".trace", "_exec.trace")
    if os.path.exists(corresp_exec_file):
        cmd = f"{TRACE_PROCESSOR_PATH} {os.path.join(results_dir, corresp_exec_file)} -Q \"SELECT name, ts, dur, depth FROM slice ORDER BY ts\" >> {target_file}"
        log("Converting exec file %s to CSV: " % cmd)
        res = execute_shell_command(cmd)
    print(res)
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
        """init the class.
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
        execute_shell_command(
            f"find {self.results_dir} -type f -name \"*.trace\"  | xargs rm ")
        execute_shell_command(
            f"find {self.results_dir} -type f -name \"*.csv\"  | xargs rm ")
        startup_output_filename = self.get_results_filename(run_id)
        log("Am Profiler run id:  %s" % run_id)
        res = execute_shell_command(" adb shell cmd package resolve-activity --brief %s | grep %s" % (self.package_name, self.package_name))
        activity_package = res[1].strip()
        cmd = " adb shell am start -S -n %s -P %s" % (activity_package, startup_output_filename )
        res = execute_shell_command(cmd)
        print(res)
        log("Profiling startup with Am Profiler: " + cmd)
        time.sleep(1)
        execute_shell_command("adb shell am profile stop %s" % self.package_name)
        time.sleep(1)
        output_filename_exec = startup_output_filename.replace(".trace", "_exec.trace")
        # adb shell am profile start --sampling 1000 com.sanad.gpt4o.myapplication /data/local/tmp/manual_startup.trace
        cmd = f"adb shell am profile start --sampling {PROFILING_SAMPLE_RATE} %s %s" % (self.package_name, output_filename_exec)
        log("Profiling exec with Am Profiler: " + cmd)
        res = execute_shell_command(cmd)
        print(res)
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
        res = execute_shell_command("adb shell am profile stop %s" % self.package_name)
        print(res)
        print('lula')
        res = execute_shell_command("adb shell find %s -type f | grep app_%s | xargs -I{} adb pull {} %s"
                                         % (DEVICE_RESULTS_DIR, self.package_name, self.results_dir))
        #res, o, e = execute_shell_command(f"adb pull {DEVICE_RESULTS_DIR}/{filename}  {self.results_dir}")
        #print(f"Pulling trace file {filename} from device: {res}, {o}, {e}")
        print(res)
        if res[0] != 0:
            print(res)
            raise Exception(f"unable to pull trace file. Attempted to pull files")
        exported_filename = self.export()
        log("Exported Am Profiler file:  %s" % exported_filename)
        return exported_filename

    def clean(self):
        """cleans device log state and removes files from previous runs.
        """
        execute_shell_command(f"adb shell rm {DEVICE_RESULTS_DIR}/*.trace")
        #execute_shell_command(
        #    f"find {self.results_dir} -type f -name \"*.trace\"  | xargs rm ")
        #execute_shell_command(
        #    f"find {self.results_dir} -type f -name \"*.csv\"  | xargs rm ")

    def export(self):
        """Exports results from previous runs.
            last_exported: path of last exported file.
        """
        log("Exporting Am Profiler results to CSV: %s" % self.results_dir)
        target_file = ""
        for f in filter(lambda x: re.match(r'app_*', x) is not None and not 'exec.trace' in x , os.listdir(self.results_dir)):
            log(f)
            f_file = os.path.join(self.results_dir, f)
            if not os.path.exists(f_file):
                raise Exception(f"trace file not found ({f_file})")
            last_exported = os.path.join(self.results_dir, f)
            #log("Converting %s to CSV: " % last_exported)
            target_file = convert_to_csv(f_file, self.results_dir)
        return target_file
