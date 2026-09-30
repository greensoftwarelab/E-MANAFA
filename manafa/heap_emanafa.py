import json
import os
import time

from manafa.parsing.heapParser import parse_heap_trace
from manafa.services.AmProfilerService import get_launcher_activity
from manafa.utils.Logger import log, LogSeverity
from manafa.utils.Utils import execute_shell_command, get_results_dir

DEVICE_TRACE_PATH = "/data/misc/perfetto-traces/manafa_heap_trace"
MIN_SDK = 30  # java_hprof requires Android 11+
# write_into_file drains the buffer to the output file every second; without it
# the buffer fills after ~4 heap graphs (~16 MB each) and DISCARD drops the rest.
CONFIG_TEMPLATE = """\
buffers: {{ size_kb: 65536  fill_policy: DISCARD }}
write_into_file: true
file_write_period_ms: 1000
data_sources: {{
  config {{
    name: "android.java_hprof"
    java_hprof_config {{
      process_cmdline: "{package}"
      continuous_dump_config {{
        dump_phase_ms: 0
        dump_interval_ms: {dump_interval_ms}
      }}
    }}
  }}
}}
"""


class HeapEManafa(object):
    """Profiles an app's Java heap: per-class instance count, shallow and retained size over time.

    Runs apart from the energy profilers: heap dumps pause the app, so capturing them during an
    energy session would bias its measurements. The app must be debuggable or profileable.

    The perfetto process is handled by PID, not name: `--background` prints the PID, which is
    killed and polled (`test -d /proc/<pid>`) at stop. `--background-wait` is avoided because it
    reparents the daemon to uid statsd, which the adb shell uid cannot signal.

    Attributes:
        app_package_name: package to profile.
        dump_interval_ms: time between heap dumps.
        results_dir: local folder where traces are pulled to.
    """
    def __init__(self, app_package_name, dump_interval_ms=5000, results_dir=os.path.join(get_results_dir(), "heap")):
        self.app_package_name = app_package_name
        self.dump_interval_ms = dump_interval_ms
        self.results_dir = results_dir
        os.makedirs(self.results_dir, exist_ok=True)
        self.pid = None
        self.trace_out_file = None
        self.heap_stats = None

    def init(self, clean=False):
        """checks that the device supports java_hprof."""
        sdk = execute_shell_command("adb shell getprop ro.build.version.sdk")[1].strip()
        if sdk.isdigit() and int(sdk) < MIN_SDK:
            raise Exception(f"device API level {sdk} < {MIN_SDK}: java_hprof requires Android 11+")

    def start(self):
        """relaunches the app and starts the heap capture (java_hprof attaches to the running process)."""
        activity = get_launcher_activity(self.app_package_name)
        execute_shell_command(f"adb shell am start -S -W -n {activity}")
        config = os.path.join(self.results_dir, "heap_config.pbtxt")
        with open(config, 'w') as f:
            f.write(CONFIG_TEMPLATE.format(package=self.app_package_name, dump_interval_ms=self.dump_interval_ms))
        res, o, e = execute_shell_command(f"cat {config} | adb shell perfetto --txt -o {DEVICE_TRACE_PATH} -c - --background")
        pid = o.strip()
        if res != 0 or not pid.isdigit():
            raise Exception(f"unable to start perfetto heap capture: {o} {e}")
        time.sleep(1)
        if not self._is_running(pid):
            raise Exception(f"perfetto (pid {pid}) exited right after starting; check the device logcat")
        self.pid = pid
        log(f"Heap capture started (perfetto pid {pid})", log_sev=LogSeverity.INFO)

    def stop(self, run_id=None):
        """stops the capture, pulls the trace and parses it. Returns the local trace path."""
        if run_id is None:
            run_id = execute_shell_command("date +%s")[1].strip()
        execute_shell_command(f"adb shell kill {self.pid}")
        for _ in range(10):
            if not self._is_running(self.pid):
                break
            time.sleep(0.5)
        else:
            raise Exception(f"perfetto (pid {self.pid}) still running after kill")
        self.trace_out_file = os.path.join(self.results_dir, f"heap-{run_id}.perfetto-trace")
        res, o, e = execute_shell_command(f"adb pull {DEVICE_TRACE_PATH} {self.trace_out_file}")
        if res != 0:
            raise Exception(f"unable to pull heap trace: {e}")
        self.heap_stats = parse_heap_trace(self.trace_out_file)
        return self.trace_out_file

    @staticmethod
    def _is_running(pid):
        return execute_shell_command(f"adb shell test -d /proc/{pid}")[0] == 0

    def save_final_report(self, output_filepath=None):
        if output_filepath is None:
            output_filepath = os.path.join(self.results_dir, "heap_report.json")
        with open(output_filepath, 'w') as j:
            json.dump({'package': self.app_package_name, 'trace_file': self.trace_out_file, **self.heap_stats}, j)
        return output_filepath
