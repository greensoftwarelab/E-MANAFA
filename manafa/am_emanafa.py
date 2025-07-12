import json
import os

from manafa.emanafa import EManafa, MANAFA_RESOURCES_DIR
from manafa.parsing.hunter.AMParser import AMParser
from manafa.services.AmProfilerService import AmProfilerService
from manafa.parsing.hunter.AppConsumptionStats import AppConsumptionStats
from manafa.utils.Logger import log, LogSeverity
from manafa.utils.Utils import execute_shell_command


class AMEManafa(EManafa):
    """Class that extends default framework behaviour, allowing to parse app traces from am prifler using AMProfilerService
    and estimate battery consumption of app components.

    Attributes:
        resources_dir: directory where aux resources are contained.
        power_profile: the power profile to be used in the profiling sessions.
        timezone: device timezone.
        unplugged: if the device is not charging.
    """
    def __init__(self,
                 app_package_name,
                 power_profile=None,
                 timezone=None,
                 resources_dir=MANAFA_RESOURCES_DIR, **kwargs):
        super(AMEManafa, self).__init__(power_profile=power_profile, timezone=timezone, resources_dir=resources_dir, **kwargs)
        self.app_consumptions = AppConsumptionStats()
        self.app_consumptions_log = ""
        self.log_service = AmProfilerService(app_package_name)
        self.am_log_parser = AMParser()
        self.trace_out_file = None

    def init(self):
        """inits inner services.
        Calls init from super class and also from the log service.
        """
        super().init()
        self.log_service.init(boot_time=self.boot_time)

    def start(self):
        """starts inner services."""
        super().start()
        self.log_service.start(self.boot_time)

    def stop(self, run_id=None):
        """stops inner services."""
        if run_id is None:
            run_id = execute_shell_command("date +%s")[1].strip()
        self.bts_out_file = self.batterystats.stop(run_id)
        self.pft_out_file = self.perfetto.stop(run_id)
        self.trace_out_file = self.log_service.stop(run_id)
        log("Perfetto file:  %s" % self.pft_out_file)
        self.parse_results(self.bts_out_file, self.pft_out_file)
        if self.unplugged:
            self.plug_back()
        return self.bts_out_file, self.pft_out_file, self.trace_out_file, self.app_consumptions_log

    def calculate_function_consumption(self, run_id=None): #, to_instrument_file, not_instrument_file):
        """calculates consumption per function called during the profiling session."""
        self.am_log_parser.parse_file(self.trace_out_file)
        run_id = os.path.basename(self.trace_out_file).split("_")[1] if self.trace_out_file is not None and run_id is None else run_id
        am_trace = self.am_log_parser.trace
        total_consumption = 0
        total_cpu_consumption = 0
        if len(self.am_log_parser.trace) == 0:
            log(f"No hunter traces found in {self.trace_out_file}", log_sev=LogSeverity.ERROR)
            return self.trace_out_file, self.app_consumptions_log
        for i, function in enumerate(am_trace):
            func_consumption = 0
            func_cpu_consumption = 0
            for j, times in enumerate(am_trace[function]):
                time = am_trace[function][j]
                begin = time['begin_time']
                if 'end_time' in time:
                    end = time['end_time']
                else:
                    end = begin
                consumption, per_component_consumption, m = self.get_consumption_in_between(begin, end)
                if consumption <= 0 or per_component_consumption['cpu'] <= 0:
                    consumption = 0.0
                    per_component_consumption.update({'cpu': 0.0})
                self.am_log_parser.add_consumption(function, j, consumption, per_component_consumption, m)
                func_consumption += consumption
                func_cpu_consumption += per_component_consumption['cpu']
            total_consumption += func_consumption
            total_cpu_consumption += func_cpu_consumption
            #self.app_consumptions.write_consumptions(consumption_log, func_cpu_consumption, function)
        #self.app_consumptions.write_consumptions(consumption_log, total_cpu_consumption)
        #hunter_edited = self.am_log_parser.add_cpu_consumption_to_trace_file(self.trace_out_file, functions, True)
        #log("Hunter file:  %s" % hunter_edited)
        self.app_consumptions.app_traces = self.am_log_parser.trace
        self.app_consumptions_log = self.app_consumptions.save_function_info(f"functions_{run_id}_results.json", filter_zeros=True)
        log("Function Consumptions file:  %s" % self.app_consumptions_log)
        return self.trace_out_file, self.app_consumptions_log

    def clean(self):
        """calls clean methods from inner services to clean previous result files"""
        super().clean()
        self.log_service.clean()
        self.app_consumptions.clean()
        self.app_consumptions_log = ""

    def parse_results(self, bts_file=None, pf_file=None, htr_file=None):
        """Given the output files from a previous session, it parses and generates results from that session."""
        super().parse_results(bts_file, pf_file)
        #pf_file = pf_file if pf_file is not None else self.pft_out_file
        #run_id = self.perfetto.get_run_id_from_perfetto_file(pf_file)
        a, b = None, None
        if len(self.bat_events.events) > 0:
            self.trace_out_file = self.trace_out_file if htr_file is None else htr_file
            a, b = self.calculate_function_consumption()
        return a, b

    def gen_final_report(self, start_time=None, end_time=None):
        begin = self.perf_events.events[0].time if start_time is None else start_time
        end = self.perf_events.events[-1].time if end_time is None else end_time
        total, per_c, timeline = self.get_consumption_in_between(begin, end)
        res = {
            'total_energy:': total,
            'elapsed_time': end - begin,
            'per_component_consumption': per_c,
            'stats': timeline,
            'method_invocations': self.app_consumptions.get_total_methods(),
            'diff_methods': self.app_consumptions.get_diff_methods()
        }
        return {
            'global': res,
            'invoked_methods': self.app_consumptions.get_elaborate_stats()
        }

    def save_final_report(self, run_id=None, output_filepath=None):
        if output_filepath is None:
            output_filepath = "manafa_resume_%s.json" % (run_id if run_id is not None else 0)
        with open(output_filepath, 'w') as j:
            json.dump(self.gen_final_report(), j)
        return output_filepath
