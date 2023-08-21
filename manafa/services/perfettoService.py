from __future__ import absolute_import

import re


from .service import Service
import time
import os

from manafa.utils.Utils import execute_shell_command, get_resources_dir

RESOURCES_DIR = get_resources_dir()

DEFAULT_OUT_DIR = "/data/misc/perfetto-traces"
CONFIG_FILE = "perfetto.config.bin"


def device_has_perfetto():
    res, o, _ = execute_shell_command("adb shell which perfetto")
    return res == 0 and 'perfetto' in o


def set_persistent_traces_enabled_flag():
    cmd = "adb shell setprop persist.traced.enable 1"
    res, o, e = execute_shell_command(cmd)
    if res != 0:
        print(e)
        raise Exception("error while setting persist.traced.enable property")


def convert_to_systrace(file_to_convert, results_dir=None):
    results_dir = results_dir if results_dir is not None else os.path.dirname(file_to_convert)
    tc_path = os.path.join(RESOURCES_DIR, 'traceconv')
    target_filename = f"{os.path.basename(file_to_convert)}.systrace"
    last_exported = os.path.join(results_dir, target_filename)
    cmd = f"chmod +x {tc_path}; {tc_path} systrace {file_to_convert} {last_exported}"
    res, o, e = execute_shell_command(cmd)
    if res != 0:
        print(cmd)
        print(o)
        raise Exception("unable to run traceconv. Hints: Maybe you need an internet connection to allow "
                        "systrace to download some resources")
    return last_exported


class PerfettoService(Service):
    """Class that manages the perfetto service.

    This class is responsible by starting and stopping the perfetto service at the start and stop of the profiiling session.
    Attributes:
        boot_time (float): timestamp of the device's last boot.
        output_res_folder (str): folder where the logs will be stored after each profiling session.
        default_out_dir(str): device default results dir.
        cfg_file(str): perfetto config file.
    """
    def __init__(self, boot_time=0, output_res_folder="perfetto", default_out_dir=DEFAULT_OUT_DIR,
                 cfg_file=CONFIG_FILE):
        Service.__init__(self, output_res_folder)
        self.cfg_file = cfg_file
        self.boot_time = boot_time
        self.output_dir = default_out_dir
        self.output_filename = os.path.join(self.output_dir, "trace")
        set_persistent_traces_enabled_flag()
        execute_shell_command(f"adb shell mkdir -p {self.output_dir}")
        self.executable_switches = {
            'background': '--background',
            'config': "--config"
        }

    def get_switch(self, key, default=""):
        return self.executable_switches[key] if key in self.executable_switches else default

    def config(self, **kwargs):
        pass

    def init(self, boot_time=0, **kwargs):
        """inits the service.
        Resets boot time and cleans files from previous runs.
        Args:
            boot_time: timestamp of the device's last boot.
            **kwargs:
        """
        self.boot_time = boot_time
        self.clean()

    def start(self):
        """start profiling session.

        Starts perfetto service, using the config file cfg_file as input.
        """
        # execute_shell_command(f"adb shell perfetto -o {self.output_filename} freq  -t 1h --background ")´
        cmd = f"cat {os.path.join(RESOURCES_DIR, self.cfg_file)} | adb shell perfetto " \
              f"{self.get_switch('background', '-b')} -o {self.output_filename} {self.get_switch('config', '-c')} -"
        print(f"executing perfetto: {cmd}")
        res, o, e = execute_shell_command(cmd=cmd)
        return res == 0 and e.strip() == ""

    def stop(self, file_id=None):
        """Stops the profiling session and exports results.

        Stops the perfetto service and pulls the results from device. Afterwards, it exports the pulled results using
        traceconv, returning the path to the last exported file as result.
        Args:
            file_id: run id.
        Returns:
            last_exported: path of last exported file.
        """
        if file_id is None:
            file_id = execute_shell_command("date +%s")[1].strip()
        res, o, e = execute_shell_command("adb shell killall perfetto")
        if res != 0:
            print(o)
            print(e)
            is_running, _, _ = execute_shell_command("adb shell ps | grep perfetto")
            if is_running:
                raise Exception("unable to kill Perfetto service")
            else:
                raise Exception("Unable to stop Perfetto because Perfetto service was not running")
        time.sleep(1)
        filename = os.path.join(self.results_dir, f'trace-{file_id}-{self.boot_time}')
        res, o, e = execute_shell_command(f"adb pull {self.output_filename} {filename}")
        if res != 0:
            raise Exception(f"unable to pull trace file. Attempted to copy {self.output_filename} to {filename}")
        return self.export()

    def export(self):
        """Exports results from previous runs.
            last_exported: path of last exported file.
        """
        last_exported = ""
        for f in filter(lambda x: re.match(r'trace-*', x) is not None, os.listdir(self.results_dir)):
            f_file = os.path.join(self.results_dir, f)
            if not os.path.exists(f_file):
                raise Exception(f"Systrace file not found ({f_file})")
            last_exported = os.path.join(self.results_dir, f"{f}.systrace")
            convert_to_systrace(f_file)
        return last_exported

    def clean(self):
        """wipe results from previous runs.
        """
        execute_shell_command(f"find {self.results_dir} -type f  | xargs rm ")
        execute_shell_command("adb shell killall perfetto")

    def get_run_id_from_perfetto_file(self, perfetto_filepath: str):
        """returns profiling session id given its filepath"""
        simple_name = os.path.basename(perfetto_filepath)
        return simple_name.split("-")[1].split(".")[0]
