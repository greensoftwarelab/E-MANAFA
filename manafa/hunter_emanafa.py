import argparse
import json
import sys
import time

from manafa.emanafa import EManafa, MANAFA_RESOURCES_DIR, has_connected_devices
from manafa.services.hunterService import HunterService
from manafa.services.appConsumptionsService import AppConsumptionsService
from manafa.utils.Logger import log, LogSeverity
from manafa.utils.Utils import execute_shell_command

MAX_SIZE = sys.maxsize
TO_INSTRUMENT_FILE = MANAFA_RESOURCES_DIR + '/to_instrument_file.txt'
NOT_INSTRUMENT_FILE = MANAFA_RESOURCES_DIR + '/not_instrument_file.txt'


class HunterEManafa(EManafa):
    def __init__(self,
                 power_profile=None,
                 timezone=None,
                 resources_dir=MANAFA_RESOURCES_DIR,
                 instrument_file=None,
                 not_instrument_file=None):
        """Inits HunterEManafa"""
        EManafa.__init__(self, power_profile=power_profile, timezone=timezone, resources_dir=resources_dir)
        self.app_consumptions = AppConsumptionsService()
        self.app_consumptions_log = None
        self.hunter = HunterService()
        self.hunter_out_file = None
        self.instrument_file = instrument_file
        self.not_instrument_file = not_instrument_file

    def init(self):
        super().init()
        self.hunter.init(boot_time=self.boot_time)
        self.app_consumptions.init(boot_time=self.boot_time)

    def start(self):
        """starts inner services"""
        super().start()
        self.hunter.start()
        self.app_consumptions.start()

    def stop(self, run_id=None):
        """starts inner services"""
        if run_id is None:
            run_id = execute_shell_command("date +%s")[1].strip()
        self.bts_out_file = self.batterystats.stop(run_id)
        self.pft_out_file = self.perfetto.stop(run_id)
        log("Perfetto file:  %s" % self.pft_out_file)
        self.parseResults(self.bts_out_file, self.pft_out_file)
        if len(self.bat_events.events) > 0:
            self.hunter_out_file = self.hunter.stop(run_id)
            # get filename to write consumptions
            self.app_consumptions_log = self.app_consumptions.stop(run_id)
        self.hunter_out_file, self.app_consumptions_log = self.calculate_function_consumption(
            self.app_consumptions_log, self.hunter_out_file, self.instrument_file, self.not_instrument_file
        )
        if self.unplugged:
            self.plug_back()
        return self.bts_out_file, self.pft_out_file, self.hunter_out_file, self.app_consumptions_log

    def calculate_function_consumption(self,
                                       consumption_log,
                                       hunterfile,
                                       to_instrument_file,
                                       not_instrument_file):

        to_instrument = False
        functions = []
        with open(to_instrument_file, 'r') as to_instrument_handle:
            functions = to_instrument_handle.read().splitlines()
            to_instrument = len(functions) == 0

        if to_instrument:
            to_instrument = False
            with open(not_instrument_file, 'r') as not_to_instrument_handle:
                functions = not_to_instrument_handle.read().splitlines()
        else:
            to_instrument = True

        self.hunter.parseFile(hunterfile, functions, to_instrument)
        hunter_trace = self.hunter.trace
        total_consumption = 0
        total_cpu_consumption = 0
        if len(self.hunter.trace) == 0:
            return
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
                if consumption < 0 or per_component_consumption['cpu'] < 0:
                    consumption = 0.0
                    per_component_consumption.update({'cpu': 0.0})
                self.hunter.addConsumption(function, j, consumption, per_component_consumption, m)
                func_consumption += consumption
                func_cpu_consumption += per_component_consumption['cpu']
            total_consumption += func_consumption
            total_cpu_consumption += func_cpu_consumption
            self.app_consumptions.write_consumptions(consumption_log, func_cpu_consumption, function)

        self.app_consumptions.write_consumptions(consumption_log, total_cpu_consumption)

        hunter_edited = self.hunter.addConsumptionToTraceFile(self.hunter_out_file, functions, to_instrument)
        log("Hunter file:  %s" % hunter_edited)
        log("Consumptions file:  %s" % self.app_consumptions_log)
        return hunter_edited, self.app_consumptions_log

    def clean(self):
        """calls clean methods from inner services to clean previous result files"""
        super().clean()
        self.hunter.clean()
        self.app_consumptions.clean()

    def parseResults(self, bts_file=None, pf_file=None, htr_file=None):
        super().parseResults(bts_file, pf_file)


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument("-p", "--profile", default=None, type=str)
    parser.add_argument("-t", "--timezone", default=None, type=str)
    parser.add_argument("-pft", "--perfettofile", default=None, type=str)
    parser.add_argument("-bts", "--batstatsfile", default=None, type=str)
    parser.add_argument("-htf", "--hunterfile", default=None, type=str)
    args = parser.parse_args()
    has_device_conn = has_connected_devices()
    invalid_file_args = (args.perfettofile is None or args.batstatsfile is None)
    if not has_device_conn and invalid_file_args:
        log("Fatal error. No connected devices and result files submitted for analysis", LogSeverity.FATAL)
        exit(-1)
    manafa = HunterEManafa(
        power_profile=args.profile,
        timezone=args.timezone,
        resources_dir=MANAFA_RESOURCES_DIR,
        instrument_file=TO_INSTRUMENT_FILE,
        not_instrument_file=NOT_INSTRUMENT_FILE
    )
    if has_device_conn and invalid_file_args:
        manafa.init()
        manafa.start()
        print("start testing...")
        time.sleep(15)  # do work
        print("stop testing...")
        manafa.stop()
    else:
        manafa.parseResults(args.batstatsfile, args.perfettofile, args.hunterfile)
    begin = manafa.perf_events.events[0].time  # first collected sample from perfetto
    end = manafa.perf_events.events[-1].time  # last collected sample from perfetto
    elapsed = end - begin
    p, c, z = manafa.getConsumptionInBetween(begin, end)
    print(p)
    print(c)
    print(z)
