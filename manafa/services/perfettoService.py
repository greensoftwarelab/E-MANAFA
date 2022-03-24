from __future__ import absolute_import

import re

from textops import cat

from .service import Service
import time
import os

from manafa.utils.Utils import execute_shell_command, get_resources_dir

RESOURCES_DIR = get_resources_dir()

DEFAULT_OUT_DIR = "/data/misc/perfetto-traces"
CONFIG_FILE = "perfetto.config.bin"


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
        execute_shell_command("adb shell setprop persist.traced.enable 1")
        execute_shell_command(f"adb shell mkdir -p {self.output_dir}")

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
        execute_shell_command(
            f"cat {os.path.join(RESOURCES_DIR, self.cfg_file)} | adb shell perfetto -d -o {self.output_filename} -c -")

    def stop(self, file_id):
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
        execute_shell_command("adb shell killall perfetto")
        time.sleep(1)
        filename = os.path.join(self.results_dir, f'trace-{file_id}-{self.boot_time}')
        execute_shell_command(f"adb pull {self.output_filename} {filename}")
        return self.export()

    def export(self):
        """Exports results from previous runs.
            last_exported: path of last exported file.
        """
        last_exported = ""
        tc_path = os.path.join(RESOURCES_DIR, 'traceconv')
        for f in filter(lambda x: re.match(r'trace-*', x) is not None, os.listdir(self.results_dir)):
            f_file = os.path.join(self.results_dir, f)
            last_exported = os.path.join(self.results_dir, f"{f}.systrace")
            res, o, e = execute_shell_command(f"chmod +x {tc_path}; {tc_path} systrace {f_file} {last_exported}")
        return last_exported

    def clean(self):
        """wipe results from previous runs.
        """
        execute_shell_command(f"find {self.results_dir} -type f  | xargs rm ")

    def get_run_id_from_perfetto_file(self, perfetto_filepath: str):
        """returns profiling session id given its filepath"""
        simple_name = os.path.basename(perfetto_filepath)
        return simple_name.split("-")[1].split(".")[0]