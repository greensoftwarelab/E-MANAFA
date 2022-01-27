import argparse
import json
import os
import sys
import time

from manafa.emanafa import EManafa, MANAFA_RESOURCES_DIR
from manafa.services.hunterService import HunterService
from manafa.hunter.AppConsumptionStats import AppConsumptionStats
from manafa.utils.Logger import log, LogSeverity
from manafa.utils.Utils import execute_shell_command

class HunterEManafa(EManafa):
    def __init__(self,
                 power_profile=None,
                 timezone=None,
                 resources_dir=MANAFA_RESOURCES_DIR,
                 instrument_file=None,
                 not_instrument_file=None):
        """Inits HunterEManafa"""
        EManafa.__init__(self, power_profile=power_profile, timezone=timezone, resources_dir=resources_dir)
        self.app_consumptions = AppConsumptionStats()
        self.app_consumptions_log = ""
        self.hunter = HunterService()
        self.hunter_out_file = None
        self.instrument_file = instrument_file
        self.not_instrument_file = not_instrument_file

    def init(self):
        super().init()
        self.hunter.init(boot_time=self.boot_time)

    def start(self):
        """starts inner services"""
        super().start()
        self.hunter.start()

    def stop(self, run_id=None):
        """starts inner services"""
        if run_id is None:
            run_id = execute_shell_command("date +%s")[1].strip()
        self.bts_out_file = self.batterystats.stop(run_id)
        self.pft_out_file = self.perfetto.stop(run_id)
        self.hunter_out_file = self.hunter.stop(run_id)
        log("Perfetto file:  %s" % self.pft_out_file)
        self.parseResults(self.bts_out_file, self.pft_out_file)
        if self.unplugged:
            self.plug_back()
        return self.bts_out_file, self.pft_out_file, self.hunter_out_file, self.app_consumptions_log

    def calculate_function_consumption(self): #, to_instrument_file, not_instrument_file):
        functions = []
        '''
        with open(to_instrument_file, 'r') as to_instrument_handle:
            functions = to_instrument_handle.read().splitlines()
            to_instrument = len(functions) == 0

        if to_instrument:
            to_instrument = False
            with open(not_instrument_file, 'r') as not_to_instrument_handle:
                functions = not_to_instrument_handle.read().splitlines()
        else:
            to_instrument = True'''
        self.hunter.parseFile(self.hunter_out_file, functions, True)
        hunter_trace = self.hunter.trace
        total_consumption = 0
        total_cpu_consumption = 0
        if len(self.hunter.trace) == 0:
            log(f"No hunter traces found in {self.hunter_out_file}", log_sev=LogSeverity.ERROR)
            return self.hunter_out_file, self.app_consumptions_log
        for i, function in enumerate(hunter_trace):
            func_consumption = 0
            func_cpu_consumption = 0
            for j, times in enumerate(hunter_trace[function]):
                time = hunter_trace[function][j]
                begin = time['begin_time']
                if 'end_time' in time:
                    end = time['end_time']
                else:
                    end = begin
                consumption, per_component_consumption, m = self.getConsumptionInBetween(begin, end)
                if consumption <= 0 or per_component_consumption['cpu'] <= 0:
                    consumption = 0.0
                    per_component_consumption.update({'cpu': 0.0})
                self.hunter.addConsumption(function, j, consumption, per_component_consumption, m)
                func_consumption += consumption
                func_cpu_consumption += per_component_consumption['cpu']
            total_consumption += func_consumption
            total_cpu_consumption += func_cpu_consumption
            #self.app_consumptions.write_consumptions(consumption_log, func_cpu_consumption, function)
        #self.app_consumptions.write_consumptions(consumption_log, total_cpu_consumption)

        hunter_edited = self.hunter.addConsumptionToTraceFile(self.hunter_out_file, functions, True)
        log("Hunter file:  %s" % hunter_edited)
        self.app_consumptions.app_traces = self.hunter.trace
        self.app_consumptions_log = self.app_consumptions.save_function_info(f"functions_{self.boot_time}_results.json", filter_zeros=True)
        log("Function Consumptions file:  %s" % self.app_consumptions_log )
        return hunter_edited, self.app_consumptions_log

    def clean(self):
        """calls clean methods from inner services to clean previous result files"""
        super().clean()
        self.hunter.clean()
        self.app_consumptions.clean()
        self.app_consumptions_log = ""

    def parseResults(self, bts_file=None, pf_file=None, htr_file=None):
        super().parseResults(bts_file, pf_file)
        #pf_file = pf_file if pf_file is not None else self.pft_out_file
        #run_id = self.perfetto.get_run_id_from_perfetto_file(pf_file)
        if len(self.bat_events.events) > 0:          
            self.hunter_out_file = self.hunter_out_file if htr_file is None else htr_file
            self.calculate_function_consumption()