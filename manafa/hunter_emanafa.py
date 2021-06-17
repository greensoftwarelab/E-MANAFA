import argparse
import time

from manafa.emanafa import EManafa, MANAFA_RESOURCES_DIR, has_connected_devices
from manafa.services.hunterService import HunterService
from manafa.utils.Logger import log, LogSeverity


class HunterEManafa(EManafa):
    def __init__(self, power_profile=None, timezone=None, resources_dir=MANAFA_RESOURCES_DIR):
        """Inits HunterEManafa"""
        EManafa.__init__(self, power_profile=None, timezone=None, resources_dir=MANAFA_RESOURCES_DIR)
        self.hunter = HunterService()
        self.hunter_out_file = None

    def init(self):
        self.hunter.init(boot_time=self.boot_time)
        super().init()

    def start(self):
        """starts inner services"""
        self.hunter.start()
        super().init()

    def stop(self):
        """starts inner services"""
        self.bts_out_file = self.batterystats.stop()
        self.pft_out_file = self.perfetto.stop()
        log("Perfetto file:  %s" % self.pft_out_file)
        self.parseResults(self.bts_out_file, self.pft_out_file)

        if len(self.bat_events.events) > 0:
            self.hunter_out_file = self.hunter.start()  # hunter start is to write to a log file (same as stop)
        self.calculate_function_consumption(self.hunter_out_file)
        if self.unplugged:
            self.__plug_back()
        return self.bts_out_file, self.pft_out_file, self.hunter_out_file

    def calculate_function_consumption(self, hunterfile):
        self.hunter.parseFile(hunterfile)
        hunter_trace = self.hunter.trace
        total_consumption = 0
        if len(self.hunter.trace)==0:
            return
        for i, function in enumerate(hunter_trace):
            func_consumption = 0
            for j, times in enumerate(hunter_trace[function]):
                time = hunter_trace[function][j]
                begin = time['begin_time']
                if 'end_time' in time:
                    end = time['end_time']
                else:
                    end = begin
                consumption, per_component_consumption, m = self.getConsumptionInBetween(begin, end)
                if consumption < 0:
                    consumption = 0.0
                self.hunter.addConsumption(function, j, consumption, per_component_consumption)
                func_consumption += consumption
            total_consumption += func_consumption
            log("Total energy consumed by %s: %f Joules" % (function, func_consumption),
                log_sev=LogSeverity.SUCCESS)
        log("Total energy consumed by APP: %f Joules" % total_consumption,
            log_sev=LogSeverity.INFO)

        hunter_edited = self.hunter.addConsumptionToTraceFile(self.hunter_out_file)
        log("Hunter file:  %s" % hunter_edited)
        return self.hunter_out_file

    def clean(self):
        """calls clean methods from inner services to clean previous result files"""
        super().clean()
        self.hunter.clean()

    def parseResults(self, bts_file=None, pf_file=None, htr_file=None):
        super().parseResults(bts_file,pf_file)



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
    g = HunterEManafa(power_profile=args.profile, timezone=args.timezone, resources_dir=MANAFA_RESOURCES_DIR)
    if has_device_conn and invalid_file_args:
        g.init()
        g.start()
        print("start testing...")
        time.sleep(7)  # do work
        print("stop testing...")
        g.stop()
    else:
        g.parseResults(args.batstatsfile, args.perfettofile,args.hunterfile)
    begin = g.bat_events.events[0].time  # first collected sample from batterystats
    end = g.bat_events.events[-1].time  # last collected sample from batterystats
    p, c, z = g.getConsumptionInBetween(begin, end)
    print("TOTAL: ")
    print(p)
    print(c)
    print(z)