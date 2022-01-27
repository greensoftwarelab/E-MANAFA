from __future__ import absolute_import

import re

from .service import Service
import time
import os

from manafa.utils.Utils import execute_shell_command, get_resources_dir

RESOURCES_DIR = get_resources_dir()

DEFAULT_OUT_DIR = "/data/misc/perfetto-traces"
CONFIG_FILE = "perfetto.config.bin"


class PerfettoService(Service):
    """docstring for BatteryStatsService"""

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
        self.boot_time = boot_time
        self.clean()

    def start(self):
        # execute_shell_command(f"adb shell perfetto -o {self.output_filename} freq  -t 1h --background ")´
        execute_shell_command(
            f"cat {os.path.join(RESOURCES_DIR, self.cfg_file)} | adb shell perfetto -d -o {self.output_filename} -c -")

    def stop(self, file_id):
        if file_id is None:
            file_id = execute_shell_command("date +%s")[1].strip()
        execute_shell_command("adb shell killall perfetto")
        time.sleep(1)
        filename = os.path.join(self.results_dir, f'trace-{file_id}-{self.boot_time}')
        execute_shell_command(f"adb pull {self.output_filename} {filename}")
        return self.export()

    def export(self):
        last_exported = ""
        for f in filter(lambda x: re.match(r'trace-*', x) is not None, os.listdir(self.results_dir)):
            res, o, e = execute_shell_command("chmod +x %s/traceconv ;"
                                              " %s/traceconv systrace %s/%s %s/%s.systrace" % (RESOURCES_DIR,
                                                                                               RESOURCES_DIR,
                                                                                               self.results_dir, f,
                                                                                               self.results_dir, f))
            last_exported = "%s/%s.systrace" % (self.results_dir, f)
        return last_exported

    def clean(self):
        execute_shell_command("find %s -type f  | xargs rm " % self.results_dir)

    def get_run_id_from_perfetto_file(self, perfetto_filepath: str):
        print(perfetto_filepath)
        simple_name = os.path.basename(perfetto_filepath)
        return simple_name.split("-")[1].split(".")[0]